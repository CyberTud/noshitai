from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import uuid
import hashlib
import redis
import json
import asyncio
import aiofiles
from celery import Celery
import stripe
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="NoShitAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:3001",
        "https://noshitai.com",
        "https://www.noshitai.com",
        "https://noshitai.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./noshitai.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    stripe_customer_id = Column(String)
    credits = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    settings = Column(JSON, default={})

class StyleProfile(Base):
    __tablename__ = "style_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    name = Column(String)
    description = Column(Text)
    parameters = Column(JSON)
    sample_text = Column(Text)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    status = Column(String, default="pending")
    input_text = Column(Text)
    output_text = Column(Text)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    watermark_id = Column(String)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class HumanizeRequest(BaseModel):
    text: str
    tone: str = Field(default="neutral", pattern="^(neutral|casual|formal|persuasive|academic)$")
    formality: float = Field(default=0.5, ge=0, le=1)
    burstiness: float = Field(default=0.5, ge=0, le=1)
    perplexity_target: int = Field(default=50, ge=1, le=100)
    idiom_density: float = Field(default=0.3, ge=0, le=1)
    conciseness: float = Field(default=0.5, ge=0, le=1)
    temperature: float = Field(default=0.7, ge=0, le=1)
    seed: Optional[int] = None
    preserve_citations: bool = True
    preserve_quotes: bool = True
    keep_language: bool = True
    max_tokens: Optional[int] = None
    style_profile_id: Optional[str] = None
    integrity_mode: str = Field(default="editor", pattern="^(editor|academic)$")

class StyleProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sample_text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/user/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_premium": current_user.is_premium,
        "credits": current_user.credits,
        "settings": current_user.settings
    }

@app.get("/api/user/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user's processing statistics
    jobs = db.query(ProcessingJob).filter(ProcessingJob.user_id == current_user.id).all()

    total_processed = len(jobs)
    completed_jobs = [j for j in jobs if j.status == "completed"]
    success_rate = (len(completed_jobs) / total_processed * 100) if total_processed > 0 else 100

    # Get recent jobs
    recent_jobs = db.query(ProcessingJob).filter(
        ProcessingJob.user_id == current_user.id
    ).order_by(ProcessingJob.created_at.desc()).limit(5).all()

    return {
        "stats": {
            "totalProcessed": total_processed,
            "creditsUsed": 10 - current_user.credits if not current_user.is_premium else 0,
            "avgProcessingTime": 2.5,  # Placeholder
            "successRate": round(success_rate, 1)
        },
        "recent_jobs": [{
            "id": job.id,
            "input_text": job.input_text[:100] if job.input_text else "",
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None
        } for job in recent_jobs]
    }

@app.get("/api/billing/history")
async def get_billing_history(current_user: User = Depends(get_current_user)):
    # Placeholder billing history
    return []

@app.post("/api/humanize")
async def humanize_text(
    request: HumanizeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_premium and current_user.credits <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    job = ProcessingJob(
        user_id=current_user.id,
        input_text=request.text,
        parameters=request.dict(),
        status="processing"
    )
    db.add(job)

    if not current_user.is_premium:
        current_user.credits -= 1

    db.commit()

    background_tasks.add_task(process_humanization, job.id, request.dict())

    return {
        "job_id": job.id,
        "status": "processing",
        "credits_remaining": current_user.credits
    }

async def process_humanization(job_id: str, parameters: dict):
    # Use the EXACT advanced humanizer with T5 models
    try:
        from humanizer_exact import ExactHumanizationEngine as HumanizationEngine
    except ImportError:
        # Fallback if dependencies not available
        from humanizer import HumanizationEngine

    db = SessionLocal()
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    try:
        # If a style profile is specified, merge its parameters
        if parameters.get('style_profile_id'):
            profile = db.query(StyleProfile).filter(
                StyleProfile.id == parameters['style_profile_id']
            ).first()

            if profile and profile.parameters:
                # Merge profile parameters with request parameters
                # Request parameters take precedence
                profile_params = profile.parameters or {}
                for key, value in profile_params.items():
                    if key not in parameters or parameters[key] is None:
                        parameters[key] = value

        engine = HumanizationEngine()
        result = engine.humanize(
            text=parameters['text'],
            **{k: v for k, v in parameters.items() if k != 'text'}
        )

        job.output_text = result['humanized_text']
        job.metrics = result['metrics']
        job.status = "completed"
        job.completed_at = datetime.utcnow()

        if parameters.get('integrity_mode') == 'academic':
            job.watermark_id = generate_watermark(result['humanized_text'])

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)

    db.commit()
    db.close()

def generate_watermark(text: str) -> str:
    return hashlib.sha256(f"{text}{datetime.utcnow()}".encode()).hexdigest()[:16]

@app.get("/api/job/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(ProcessingJob).filter(
        ProcessingJob.id == job_id,
        ProcessingJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "status": job.status,
        "input_text": job.input_text,
        "output_text": job.output_text,
        "metrics": job.metrics,
        "parameters": job.parameters,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "error_message": job.error_message,
        "watermark_id": job.watermark_id
    }

@app.post("/api/style-profiles")
async def create_style_profile(
    profile: StyleProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use OpenAI-powered analyzer if API key is available
    if os.getenv('OPENAI_API_KEY'):
        from humanizer_openai import analyze_style
    else:
        from humanizer import analyze_style

    metrics = analyze_style(profile.sample_text)

    # Extract parameters from metrics to use as defaults
    parameters = {
        'formality': min(1.0, metrics.get('formal_words', 0.5)),
        'burstiness': min(1.0, metrics.get('sentence_length_variance', 10) / 20),
        'conciseness': 1 - min(1.0, metrics.get('avg_sentence_length', 15) / 30),
        'lexical_diversity': metrics.get('lexical_diversity', 0.5)
    }

    db_profile = StyleProfile(
        user_id=current_user.id,
        name=profile.name,
        description=profile.description,
        sample_text=profile.sample_text,
        metrics=metrics,
        parameters=parameters
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return {
        "id": db_profile.id,
        "name": db_profile.name,
        "description": db_profile.description,
        "metrics": db_profile.metrics,
        "created_at": db_profile.created_at
    }

@app.get("/api/style-profiles")
async def list_style_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profiles = db.query(StyleProfile).filter(
        StyleProfile.user_id == current_user.id
    ).all()

    return [{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "metrics": p.metrics,
        "created_at": p.created_at
    } for p in profiles]

@app.delete("/api/style-profiles/{profile_id}")
async def delete_style_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StyleProfile).filter(
        StyleProfile.id == profile_id,
        StyleProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()
    return {"message": "Profile deleted successfully"}

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    content = await file.read()

    if file.filename.endswith('.txt'):
        text = content.decode('utf-8')
    elif file.filename.endswith('.docx'):
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        text = '\n'.join([p.text for p in doc.paragraphs])
    elif file.filename.endswith('.pdf'):
        import PyPDF2
        import io
        pdf = PyPDF2.PdfReader(io.BytesIO(content))
        text = '\n'.join([page.extract_text() for page in pdf.pages])
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    return {"text": text}

@app.post("/api/billing/subscribe")
async def create_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")

    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name
        )
        current_user.stripe_customer_id = customer.id
        db.commit()

    checkout_session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': os.getenv('STRIPE_PRICE_ID'),
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:3000/success',
        cancel_url='http://localhost:3000/cancel',
    )

    return {"checkout_url": checkout_session.url}

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: dict, db: Session = Depends(get_db)):
    if request['type'] == 'checkout.session.completed':
        session = request['data']['object']
        customer_id = session['customer']

        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()

        if user:
            user.is_premium = True
            db.commit()

    return {"status": "success"}

@app.get("/")
async def root():
    return {"name": "NoShitAI API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)