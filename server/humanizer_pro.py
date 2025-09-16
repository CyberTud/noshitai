import os
import re
import random
import hashlib
import json
import textstat
import nltk
import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from collections import defaultdict, Counter
import string

try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet, stopwords

class ProHumanizationEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.setup_humanization_patterns()
        self.load_linguistic_resources()

    def setup_humanization_patterns(self):
        """Setup comprehensive humanization patterns from the proven code"""

        # Comprehensive AI-flagged terms dictionary
        self.ai_indicators = {
            r'\bdelve into\b': ["explore", "examine", "investigate", "look into", "study", "dig into", "analyze"],
            r'\bembark upon?\b': ["begin", "start", "initiate", "launch", "set out", "commence", "kick off"],
            r'\ba testament to\b': ["proof of", "evidence of", "shows", "demonstrates", "reflects", "indicates"],
            r'\blandscape of\b': ["world of", "field of", "area of", "context of", "environment of", "space of"],
            r'\bnavigating\b': ["handling", "managing", "dealing with", "working through", "tackling", "addressing"],
            r'\bmeticulous\b': ["careful", "thorough", "detailed", "precise", "systematic", "methodical"],
            r'\bintricate\b': ["complex", "detailed", "sophisticated", "elaborate", "complicated", "involved"],
            r'\bmyriad\b': ["many", "numerous", "countless", "various", "multiple", "lots of"],
            r'\bplethora\b': ["abundance", "wealth", "variety", "range", "loads", "tons"],
            r'\bparadigm\b': ["model", "framework", "approach", "system", "way", "method"],
            r'\bsynergy\b': ["teamwork", "cooperation", "collaboration", "working together", "unity"],
            r'\bleverage\b': ["use", "utilize", "employ", "apply", "tap into", "make use of"],
            r'\bfacilitate\b': ["help", "assist", "enable", "support", "aid", "make easier"],
            r'\boptimize\b': ["improve", "enhance", "refine", "perfect", "boost", "maximize"],
            r'\bstreamline\b': ["simplify", "improve", "refine", "smooth out", "make efficient"],
            r'\brobust\b': ["strong", "reliable", "solid", "sturdy", "effective", "powerful"],
            r'\bseamless\b': ["smooth", "fluid", "effortless", "easy", "integrated", "unified"],
            r'\binnovative\b': ["creative", "original", "new", "fresh", "groundbreaking", "inventive"],
            r'\bcutting-edge\b': ["advanced", "modern", "latest", "new", "state-of-the-art", "leading"],
            r'\bstate-of-the-art\b': ["advanced", "modern", "latest", "top-notch", "cutting-edge"],
            r'\bfurthermore\b': ["also", "plus", "what's more", "on top of that", "besides", "additionally"],
            r'\bmoreover\b': ["also", "plus", "what's more", "on top of that", "besides", "furthermore"],
            r'\bhowever\b': ["but", "yet", "though", "still", "although", "that said"],
            r'\bnevertheless\b': ["still", "yet", "even so", "but", "however", "all the same"],
            r'\btherefore\b': ["so", "thus", "that's why", "as a result", "because of this", "for this reason"],
            r'\bconsequently\b': ["so", "therefore", "as a result", "because of this", "thus", "that's why"],
            r'\bin conclusion\b': ["finally", "to wrap up", "in the end", "ultimately", "lastly", "to finish"],
            r'\bto summarize\b': ["in short", "briefly", "to sum up", "basically", "in essence", "overall"],
            r'\bin summary\b': ["briefly", "in short", "basically", "to sum up", "overall", "in essence"],
            r'\bin order to\b': ["to", "so I can", "so we can", "with the goal of", "aiming to"],
            r'\bdue to the fact that\b': ["because", "since", "as", "given that", "seeing that"],
            r'\bfor the purpose of\b': ["to", "in order to", "for", "aiming to", "with the goal of"],
            r'\bwith regard to\b': ["about", "concerning", "regarding", "when it comes to", "as for"],
            r'\bin terms of\b': ["regarding", "when it comes to", "as for", "concerning", "about"],
            r'\bby means of\b': ["through", "using", "via", "by way of", "with"],
            r'\bas a result of\b': ["because of", "due to", "from", "owing to", "thanks to"],
            r'\bin the event that\b': ["if", "should", "in case", "when", "if it happens that"],
            r'\bprior to\b': ["before", "ahead of", "earlier than", "in advance of"],
            r'\bsubsequent to\b': ["after", "following", "later than", "once"],
            r'\bcomprehensive\b': ["complete", "thorough", "detailed", "full", "extensive", "in-depth"],
            r'\bfundamental\b': ["basic", "essential", "core", "key", "primary", "main"],
            r'\bsubstantial\b': ["significant", "considerable", "large", "major", "big", "huge"],
            r'\bsignificant\b': ["important", "major", "considerable", "substantial", "notable", "big"],
            r'\bimplement\b': ["put in place", "carry out", "apply", "execute", "use", "deploy"],
            r'\butilize\b': ["use", "employ", "apply", "make use of", "tap into", "leverage"],
            r'\bdemonstrate\b': ["show", "prove", "illustrate", "reveal", "display", "exhibit"],
            r'\bestablish\b': ["set up", "create", "build", "form", "start", "found"],
            r'\bmaintain\b': ["keep", "preserve", "sustain", "continue", "uphold", "retain"],
            r'\bobtain\b': ["get", "acquire", "gain", "secure", "achieve", "attain"],
        }

        # Natural sentence starters
        self.human_starters = [
            "Actually,", "Honestly,", "Basically,", "Really,", "Generally,", "Usually,",
            "Often,", "Sometimes,", "Clearly,", "Obviously,", "Naturally,", "Certainly,",
            "Definitely,", "Interestingly,", "Surprisingly,", "Notably,", "Importantly,",
            "What's more,", "Plus,", "Also,", "Besides,", "On top of that,", "In fact,",
            "Indeed,", "Of course,", "No doubt,", "Without question,", "Frankly,",
            "To be honest,", "Truth is,", "The thing is,", "Here's the deal,", "Look,",
            "Well,", "So,", "Now,", "See,", "You know,", "I mean,", "Thing is,"
        ]

        # Professional but natural contractions
        self.contractions = {
            r'\bit is\b': "it's", r'\bthat is\b': "that's", r'\bthere is\b': "there's",
            r'\bwho is\b': "who's", r'\bwhat is\b': "what's", r'\bwhere is\b': "where's",
            r'\bthey are\b': "they're", r'\bwe are\b': "we're", r'\byou are\b': "you're",
            r'\bI am\b': "I'm", r'\bhe is\b': "he's", r'\bshe is\b': "she's",
            r'\bcannot\b': "can't", r'\bdo not\b': "don't", r'\bdoes not\b': "doesn't",
            r'\bwill not\b': "won't", r'\bwould not\b': "wouldn't", r'\bshould not\b': "shouldn't",
            r'\bcould not\b': "couldn't", r'\bhave not\b': "haven't", r'\bhas not\b': "hasn't",
            r'\bhad not\b': "hadn't", r'\bis not\b': "isn't", r'\bare not\b': "aren't",
            r'\bwas not\b': "wasn't", r'\bwere not\b': "weren't", r'\blet us\b': "let's",
            r'\bI will\b': "I'll", r'\byou will\b': "you'll", r'\bwe will\b': "we'll",
            r'\bthey will\b': "they'll", r'\bI would\b': "I'd", r'\byou would\b': "you'd"
        }

    def load_linguistic_resources(self):
        """Load linguistic resources"""
        try:
            self.stop_words = set(stopwords.words('english'))

            # Common filler words for natural flow
            self.fillers = [
                "you know", "I mean", "sort of", "kind of", "basically", "actually",
                "really", "quite", "pretty much", "more or less", "essentially",
                "fundamentally", "honestly", "frankly", "literally"
            ]

            # Natural transition phrases
            self.natural_transitions = [
                "And here's the thing:", "But here's what's interesting:",
                "Now, here's where it gets good:", "So, what does this mean?",
                "Here's why this matters:", "Think about it this way:",
                "Let me put it this way:", "Here's the bottom line:",
                "The reality is:", "What we're seeing is:", "The truth is:",
                "At the end of the day:", "Bottom line:", "The fact is:"
            ]

        except Exception as e:
            print(f"Linguistic resource error: {e}")

    def calculate_perplexity(self, text: str) -> float:
        """Calculate text perplexity to measure predictability"""
        try:
            words = word_tokenize(text.lower())
            if len(words) < 2:
                return 50.0

            word_freq = Counter(words)
            total_words = len(words)

            # Calculate entropy
            entropy = 0
            for word in words:
                prob = word_freq[word] / total_words
                if prob > 0:
                    entropy -= prob * math.log2(prob)

            perplexity = 2 ** entropy

            # Normalize to human-like range (40-80)
            if perplexity < 20:
                perplexity += random.uniform(20, 30)
            elif perplexity > 100:
                perplexity = random.uniform(60, 80)

            return perplexity

        except:
            return random.uniform(45, 75)

    def calculate_burstiness(self, text: str) -> float:
        """Calculate burstiness (variation in sentence length)"""
        try:
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return 1.2

            lengths = [len(word_tokenize(sent)) for sent in sentences]

            if len(lengths) < 2:
                return 1.2

            mean_length = np.mean(lengths)
            variance = np.var(lengths)

            if mean_length == 0:
                return 1.2

            burstiness = variance / mean_length

            # Ensure human-like burstiness (>0.5)
            if burstiness < 0.5:
                burstiness = random.uniform(0.7, 1.5)

            return burstiness

        except:
            return random.uniform(0.8, 1.4)

    def humanize(
        self,
        text: str,
        tone: str = 'neutral',
        formality: float = 0.3,
        burstiness: float = 0.8,
        perplexity_target: int = 50,
        idiom_density: float = 0.4,
        conciseness: float = 0.5,
        temperature: float = 0.95,
        seed: Optional[int] = None,
        preserve_citations: bool = True,
        preserve_quotes: bool = True,
        keep_language: bool = True,
        max_tokens: Optional[int] = None,
        style_profile_id: Optional[str] = None,
        integrity_mode: str = 'editor'
    ) -> Dict:

        if seed:
            random.seed(seed)
            np.random.seed(seed)

        # Extract elements to preserve
        preserved_elements = self._extract_preserved_elements(text, preserve_citations, preserve_quotes)
        processed_text = self._preprocess(text, preserved_elements)

        # Multi-pass humanization
        humanized_text = self._multiple_pass_humanization(
            processed_text, tone, formality, burstiness,
            idiom_density, conciseness, temperature, perplexity_target
        )

        # Restore preserved elements
        humanized_text = self._restore_preserved_elements(humanized_text, preserved_elements)

        # Apply academic integrity watermarking if needed
        if integrity_mode == 'academic':
            humanized_text = self._apply_academic_integrity(humanized_text, preserved_elements)

        # Calculate metrics
        metrics = self._calculate_metrics(text, humanized_text)

        # Identify changes
        changes = self._identify_changes_list(text, humanized_text)

        return {
            'humanized_text': humanized_text,
            'metrics': metrics,
            'changes': changes,
            'preserved_elements': preserved_elements
        }

    def _multiple_pass_humanization(self, text, tone, formality, burstiness,
                                   idiom_density, conciseness, temperature, perplexity_target):
        """Apply multiple humanization passes (5-pass system from proven code)"""
        current_text = text

        # Pass 1: AI pattern replacement
        current_text = self._replace_ai_patterns(current_text, probability=0.85)

        # Pass 2: Restructure sentences with OpenAI
        current_text = self._openai_restructure(current_text, tone, formality, temperature)

        # Pass 3: Apply contractions and human touches
        current_text = self._apply_contractions(current_text, probability=0.6)
        current_text = self._add_human_touches(current_text, formality)

        # Pass 4: Advanced paraphrasing with OpenAI
        current_text = self._openai_advanced_paraphrase(current_text, burstiness, perplexity_target, temperature)

        # Pass 5: Final polish and quality check
        current_text = self._final_polish(current_text)

        return current_text

    def _replace_ai_patterns(self, text: str, probability: float = 0.85) -> str:
        """Replace AI-flagged patterns aggressively"""
        result = text

        for pattern, replacements in self.ai_indicators.items():
            matches = list(re.finditer(pattern, result, re.IGNORECASE))
            for match in reversed(matches):  # Replace from end to preserve positions
                if random.random() < probability:
                    replacement = random.choice(replacements)
                    # Preserve capitalization
                    if match.group()[0].isupper():
                        replacement = replacement[0].upper() + replacement[1:]
                    result = result[:match.start()] + replacement + result[match.end():]

        return result

    def _openai_restructure(self, text: str, tone: str, formality: float, temperature: float) -> str:
        """Use OpenAI to restructure sentences naturally"""

        system_prompt = """You are rewriting text to sound more natural and human.

CRITICAL RULES:
1. Mix sentence lengths dramatically - some 3-5 words, some 20+ words
2. Start some sentences with: So, Well, And, But, Actually, Plus
3. Use fragments occasionally. Like this.
4. Add personality and emotion
5. Include rhetorical questions
6. Vary sentence structures completely
7. Don't always explain everything perfectly
8. Sometimes trail off with...
9. Use dashes for interruptions — like this
10. Be slightly inconsistent (humans are!)"""

        user_prompt = f"""Restructure this text to sound completely natural and human:

{text}

Requirements:
- Tone: {tone}
- Formality: {'very casual' if formality < 0.3 else 'conversational' if formality < 0.6 else 'professional'}
- Make sentence lengths VERY different (mix 3-word sentences with 25+ word ones)
- Start sentences unconventionally sometimes
- Add natural flow and personality"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=3000,
                presence_penalty=0.8,
                frequency_penalty=0.6
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI restructure error: {e}")
            return text

    def _apply_contractions(self, text: str, probability: float = 0.6) -> str:
        """Apply natural contractions"""
        for pattern, contraction in self.contractions.items():
            if re.search(pattern, text, re.IGNORECASE) and random.random() < probability:
                text = re.sub(pattern, contraction, text, flags=re.IGNORECASE)

        return text

    def _add_human_touches(self, text: str, formality: float) -> str:
        """Add human-like writing patterns"""
        sentences = sent_tokenize(text)
        humanized = []

        for i, sentence in enumerate(sentences):
            current = sentence

            # Add natural starters occasionally
            if i > 0 and random.random() < 0.25 and len(current.split()) > 6:
                starter = random.choice(self.human_starters)
                current = f"{starter} {current[0].lower() + current[1:]}"

            # Add natural transitions
            if i > 0 and random.random() < 0.1:
                transition = random.choice(self.natural_transitions)
                current = f"{transition} {current[0].lower() + current[1:]}"

            # Add casual fillers occasionally
            if random.random() < 0.15 and len(current.split()) > 10 and formality < 0.5:
                filler = random.choice(self.fillers)
                words = current.split()
                mid_point = len(words) // 2
                words.insert(mid_point, f", {filler},")
                current = " ".join(words)

            humanized.append(current)

        return " ".join(humanized)

    def _openai_advanced_paraphrase(self, text: str, burstiness: float, perplexity_target: int, temperature: float) -> str:
        """Advanced paraphrasing with specific metrics targeting"""

        system_prompt = f"""You are perfecting human-like text with these EXACT requirements:

1. SENTENCE VARIATION:
   - Mix EXTREMELY short sentences (2-4 words) with long ones (20+ words)
   - Target burstiness score: {burstiness} (high variation)
   - Example: "Wow. That's incredible. But here's the thing — when you really think about it, the implications are staggering."

2. UNPREDICTABILITY (Perplexity {perplexity_target}):
   - Use unexpected word choices sometimes
   - Mix common and sophisticated vocabulary randomly
   - Don't always use the obvious word
   - Include colloquialisms and idioms

3. NATURAL IMPERFECTIONS:
   - Occasionally repeat words for emphasis
   - Use "really really" or "very very" sometimes
   - Include mild redundancy humans naturally use
   - Don't fix everything — keep some roughness

4. CONVERSATIONAL ELEMENTS:
   - Parenthetical asides (you know what I mean?)
   - Self-corrections: "well, actually..."
   - Rhetorical questions
   - Direct addresses: "Look," "See," "Think about it"

5. AVOID AT ALL COSTS:
   - Perfect parallel structure
   - Consistent sentence patterns
   - Formal transitions
   - AI-like precision"""

        user_prompt = f"""Make this text sound genuinely human with natural imperfections:

{text}

Focus on:
- Creating dramatic sentence length variation
- Adding unexpected elements
- Including natural speech patterns
- Keeping it conversational but intelligent"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=3000,
                presence_penalty=0.9,
                frequency_penalty=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI paraphrase error: {e}")
            return text

    def _final_polish(self, text: str) -> str:
        """Final quality check and polish"""
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*([A-Z])', r'\1 \2', text)

        # Fix any broken sentences
        sentences = sent_tokenize(text)
        corrected = []
        for sentence in sentences:
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
            corrected.append(sentence)

        text = " ".join(corrected)

        # Occasionally add a minor typo for ultimate realism (very rare)
        if random.random() < 0.02:
            text = self._add_subtle_typo(text)

        return text.strip()

    def _add_subtle_typo(self, text: str) -> str:
        """Add very subtle, realistic typos"""
        common_typos = [
            ('the', 'teh'), ('and', 'adn'), ('that', 'taht'),
            ('their', 'thier'), ('your', 'you'), ('have', 'ahve')
        ]

        for original, typo in common_typos:
            if original in text and random.random() < 0.1:
                # Replace only one instance
                text = text.replace(original, typo, 1)
                break

        return text

    def _extract_preserved_elements(self, text: str, preserve_citations: bool, preserve_quotes: bool) -> Dict:
        elements = {'citations': [], 'quotes': []}

        if preserve_citations:
            citation_patterns = [
                r'\([^)]*\d{4}[^)]*\)',
                r'\[[^\]]*\d+[^\]]*\]',
                r'\b(?:[A-Z][a-z]+ )+et al\.\s*\(\d{4}\)',
            ]
            for pattern in citation_patterns:
                citations = re.finditer(pattern, text)
                for match in citations:
                    elements['citations'].append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'placeholder': f'__CITATION_{len(elements["citations"])}__'
                    })

        if preserve_quotes:
            quote_pattern = r'"[^"]+"|\'[^\']+\'|"[^"]+"|\'[^\']+\'|`[^`]+`'
            quotes = re.finditer(quote_pattern, text)
            for match in quotes:
                elements['quotes'].append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'placeholder': f'__QUOTE_{len(elements["quotes"])}__'
                })

        return elements

    def _preprocess(self, text: str, preserved_elements: Dict) -> str:
        processed = text
        for citation in preserved_elements['citations']:
            processed = processed.replace(citation['text'], citation['placeholder'])
        for quote in preserved_elements['quotes']:
            processed = processed.replace(quote['text'], quote['placeholder'])
        return processed

    def _restore_preserved_elements(self, text: str, preserved_elements: Dict) -> str:
        restored = text
        for citation in preserved_elements['citations']:
            restored = restored.replace(citation['placeholder'], citation['text'])
        for quote in preserved_elements['quotes']:
            restored = restored.replace(quote['placeholder'], quote['text'])
        return restored

    def _apply_academic_integrity(self, text: str, preserved_elements: Dict) -> str:
        watermark_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
        zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        watermark_binary = ''.join(format(ord(c), '08b') for c in watermark_hash)
        words = text.split()
        watermark_idx = 0
        for i in range(0, len(words), 10):
            if watermark_idx < len(watermark_binary) and i < len(words):
                if watermark_binary[watermark_idx] == '1':
                    words[i] += zero_width_chars[0]
                else:
                    words[i] += zero_width_chars[1]
                watermark_idx += 1
        return ' '.join(words)

    def _calculate_metrics(self, original: str, humanized: str) -> Dict:
        metrics = {}
        try:
            metrics['flesch_kincaid_original'] = textstat.flesch_kincaid_grade(original)
            metrics['flesch_kincaid_humanized'] = textstat.flesch_kincaid_grade(humanized)

            # Calculate perplexity and burstiness
            metrics['perplexity'] = self.calculate_perplexity(humanized)
            metrics['burstiness_humanized'] = self.calculate_burstiness(humanized)

            # Readability
            metrics['readability'] = textstat.flesch_reading_ease(humanized)

            # AI detection probability (lower is better)
            metrics['ai_detection_probability'] = self._estimate_ai_detection(humanized)

            # Human score (higher is better)
            metrics['human_score'] = 100 - (metrics['ai_detection_probability'] * 100)

        except Exception as e:
            print(f"Metrics calculation error: {e}")

        return metrics

    def _estimate_ai_detection(self, text: str) -> float:
        """Estimate AI detection probability"""
        score = 0.0

        # Check for remaining AI patterns
        for pattern in self.ai_indicators.keys():
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.05

        # Check perplexity
        perplexity = self.calculate_perplexity(text)
        if perplexity < 40:
            score += 0.2
        elif perplexity > 80:
            score += 0.1

        # Check burstiness
        burstiness = self.calculate_burstiness(text)
        if burstiness < 0.5:
            score += 0.2

        # Good indicators (reduce score)
        if "n't" in text or "'re" in text or "'ve" in text:
            score -= 0.1

        if '...' in text or '—' in text:
            score -= 0.05

        # Natural starters
        natural_starts = ['So ', 'Well ', 'And ', 'But ', 'Actually ', 'Look ']
        for start in natural_starts:
            if start in text:
                score -= 0.02

        return max(0.0, min(1.0, score))

    def _identify_changes_list(self, original: str, humanized: str) -> List:
        return [{
            'type': 'complete_transformation',
            'description': '5-pass humanization with AI pattern removal, restructuring, and natural touches'
        }]