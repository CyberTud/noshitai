# NoShitAI - AI Text Humanizer

Transform AI-generated text into natural human prose with advanced controls and ethical safeguards.

## Features

- **Text Humanization**: Advanced engine that transforms AI text into natural human writing
- **Adjustable Parameters**: Control tone, formality, burstiness, perplexity, idiom density, and more
- **Style Profiles**: Create custom writing styles from sample texts
- **Academic Integrity Mode**: Preserve citations/quotes with invisible watermarking
- **Batch Processing**: Process multiple documents with consistent settings
- **File Support**: Upload TXT, DOCX, and PDF files
- **Detailed Metrics**: Track perplexity, burstiness, readability scores
- **Authentication & Billing**: User accounts with Stripe integration
- **Real-time Processing**: Live preview with diff visualization

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Redis (Cache & queue)
- Celery (Background tasks)
- Stripe (Payments)

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts

**AI/NLP:**
- spaCy
- NLTK
- Transformers (GPT-2)
- TextStat

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/CyberTud/noshitai.git
cd noshitai
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Install backend dependencies:
```bash
cd server
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Install frontend dependencies:
```bash
cd ../client
npm install
```

5. Start the development servers:
```bash
# From root directory
npm install
npm run dev
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000

### Using Docker

```bash
docker-compose up
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile

### Humanization
- `POST /api/humanize` - Humanize text
- `GET /api/job/{job_id}` - Get job status
- `POST /api/upload` - Upload file

### Style Profiles
- `GET /api/style-profiles` - List profiles
- `POST /api/style-profiles` - Create profile
- `DELETE /api/style-profiles/{id}` - Delete profile

### Billing
- `POST /api/billing/subscribe` - Create subscription
- `POST /api/webhook/stripe` - Stripe webhook

## Configuration

### Parameters

- **Tone**: neutral, casual, formal, persuasive, academic
- **Formality**: 0.0 (informal) to 1.0 (formal)
- **Burstiness**: 0.0 (uniform) to 1.0 (varied sentence length)
- **Perplexity Target**: 1-100 (complexity level)
- **Idiom Density**: 0.0 (none) to 1.0 (frequent)
- **Conciseness**: 0.0 (verbose) to 1.0 (concise)
- **Temperature**: 0.0 (conservative) to 1.0 (creative)

### Integrity Modes

- **Editor Mode**: Standard humanization for quality improvement
- **Academic Mode**: Preserves citations/quotes, adds watermark

## Deployment

### Production Setup

1. Set production environment variables
2. Use production database (PostgreSQL)
3. Configure Stripe webhooks
4. Set up SSL certificates
5. Use production WSGI server (Gunicorn/Uvicorn)

### Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379
SECRET_KEY=strong-secret-key
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PRICE_ID=price_xxx
```

## License

Proprietary - All rights reserved

## Support

For support, email support@noshitai.com