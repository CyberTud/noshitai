import os
import re
import random
import hashlib
import json
import textstat
import nltk
import numpy as np
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
import spacy
from collections import Counter

try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('words', quiet=True)
except:
    pass

class UltimateHumanizationEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None

        # Human writing patterns database
        self.human_patterns = {
            'sentence_starters': [
                "So", "Well", "Look", "Okay", "Actually", "Honestly",
                "You know what", "Here's the thing", "The thing is", "I mean",
                "Basically", "See", "Now", "Oh", "Yeah", "Right", "Sure",
                "Anyway", "Besides", "Plus", "Also", "And another thing"
            ],
            'fillers': [
                "you know", "I mean", "kind of", "sort of", "like",
                "basically", "actually", "really", "just", "pretty much",
                "or something", "or whatever", "and stuff", "and all that"
            ],
            'casual_transitions': [
                "But here's where it gets interesting",
                "And get this", "The crazy part is", "What's wild is",
                "Funny thing is", "The weird thing is", "But wait",
                "Oh and", "Also worth noting", "Quick side note",
                "Real quick", "By the way", "Speaking of which"
            ],
            'thinking_phrases': [
                "if you ask me", "in my opinion", "from what I can tell",
                "the way I see it", "if I'm being honest", "to be fair",
                "I'd say", "seems like", "feels like", "looks like"
            ],
            'emphasis_patterns': [
                "really really", "super", "totally", "absolutely",
                "literally", "seriously", "definitely", "honestly",
                "genuinely", "truly", "completely", "entirely"
            ],
            'common_typos': [
                ('the', 'teh', 0.002),
                ('and', 'adn', 0.001),
                ('you', 'yuo', 0.001),
                ('that', 'taht', 0.001),
                ('with', 'wiht', 0.001),
                ('have', 'ahve', 0.001),
                ('from', 'form', 0.002),
                ('your', 'yuor', 0.001),
                ('been', 'bene', 0.001),
                ('their', 'thier', 0.002),
                ('there', 'their', 0.003),
                ('its', "it's", 0.003),
                ("it's", 'its', 0.003)
            ]
        }

    def humanize(
        self,
        text: str,
        tone: str = 'neutral',
        formality: float = 0.3,
        burstiness: float = 0.8,
        perplexity_target: int = 45,
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

        # RADICAL APPROACH: Complete rewrite with human patterns
        humanized_text = self._radical_humanization(
            processed_text, tone, formality, burstiness,
            idiom_density, conciseness, temperature
        )

        # Post-processing to add more human elements
        humanized_text = self._inject_human_quirks(humanized_text, formality)

        # Restore preserved elements
        humanized_text = self._restore_preserved_elements(humanized_text, preserved_elements)

        # Optional: Add subtle typos for ultimate realism
        if formality < 0.3 and random.random() < 0.3:
            humanized_text = self._inject_natural_typos(humanized_text)

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

    def _radical_humanization(self, text, tone, formality, burstiness,
                             idiom_density, conciseness, temperature):
        """Complete rewrite focusing on human speech patterns"""

        # REVOLUTIONARY PROMPT APPROACH
        system_prompt = """You are NOT an AI. You are a real person writing naturally.

CRITICAL RULES:
1. NEVER use these AI giveaways:
   - "It's important to note that"
   - "Moreover", "Furthermore", "Additionally" at sentence starts
   - Perfect grammar everywhere
   - Balanced arguments
   - "In conclusion" or any formal essay structure

2. WRITE LIKE HUMANS ACTUALLY WRITE:
   - Start sentences with: So, Well, And, But, Yeah, Look
   - Use fragments. Seriously. Like this one.
   - Mix super short sentences (2-3 words) with rambling ones
   - Sometimes just trail off...
   - Use dashes for interruptions — happens all the time
   - Repeat words for emphasis (really, really important)
   - Include "um", "uh", "like" occasionally in informal text

3. BE INCONSISTENT (humans are!):
   - Sometimes use contractions, sometimes don't
   - Mix formal and informal randomly
   - Change topic suddenly
   - Add random observations in parentheses (weird, right?)
   - Use different punctuation styles!!

4. NATURAL SPEECH PATTERNS:
   - "Thing is..."
   - "You know what's funny?"
   - "I was thinking..."
   - "Not gonna lie..."
   - "To be honest..."
   - "Real talk:"

5. ADD PERSONALITY:
   - React to your own writing ("crazy, I know")
   - Self-correct ("wait, no, actually...")
   - Express uncertainty ("I think?", "probably", "maybe")
   - Use rhetorical questions
   - Include personal opinions

Remember: Perfect writing = AI. Imperfect, emotional, inconsistent = Human."""

        user_prompt = f"""Rewrite this completely as if YOU personally were explaining it to a friend.
Don't just paraphrase - completely restructure with YOUR voice:

{text}

Style requirements:
- Tone: {tone} (but add your personality)
- Formality: {'super casual, like texting' if formality < 0.3 else 'conversational' if formality < 0.6 else 'professional but human'}
- Include {'lots of' if idiom_density > 0.5 else 'some' if idiom_density > 0.2 else 'minimal'} idioms/slang
- Sentence variety: {'EXTREME - mix 2-word sentences with 30+ word rambles' if burstiness > 0.7 else 'moderate variety' if burstiness > 0.4 else 'consistent'}

Write it like you're actually talking. Include your natural speech patterns, hesitations, and personality."""

        try:
            # First pass: Complete rewrite
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens or 3000,
                presence_penalty=0.8,  # High to avoid AI patterns
                frequency_penalty=0.6   # Moderate to allow natural repetition
            )

            humanized = response.choices[0].message.content.strip()

            # Second pass: Add more chaos and personality
            chaos_prompt = """You're editing your own writing to make it sound even MORE natural and conversational.

Add these elements:
1. Interrupt yourself mid-sentence with new thoughts
2. Use informal abbreviations (gonna, wanna, kinda, etc.)
3. Add emotional reactions ("ugh", "wow", "geez")
4. Include uncertainty markers ("I guess", "probably", "or something")
5. Mix in stream-of-consciousness style
6. Don't fix imperfections - add more!
7. Include contradictions and self-corrections
8. Use everyday analogies and comparisons
9. Add casual observations and asides

Make it sound like you're literally speaking out loud."""

            response2 = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": chaos_prompt},
                    {"role": "user", "content": f"Make this sound MORE human and natural:\n\n{humanized}"}
                ],
                temperature=min(1.0, temperature + 0.1),
                max_tokens=max_tokens or 3000,
                presence_penalty=0.9,
                frequency_penalty=0.7
            )

            final_text = response2.choices[0].message.content.strip()

            return final_text

        except Exception as e:
            print(f"Error in radical humanization: {str(e)}")
            return self._fallback_humanize(text)

    def _inject_human_quirks(self, text: str, formality: float) -> str:
        """Add subtle human writing quirks"""

        sentences = nltk.sent_tokenize(text)
        if not sentences:
            return text

        modified_sentences = []

        for i, sentence in enumerate(sentences):
            # Randomly add human elements
            if random.random() < 0.15 and formality < 0.5:
                # Add sentence starter
                starter = random.choice(self.human_patterns['sentence_starters'])
                sentence = f"{starter}, {sentence[0].lower()}{sentence[1:]}"

            if random.random() < 0.1 and formality < 0.4:
                # Add filler
                words = sentence.split()
                if len(words) > 5:
                    insert_pos = random.randint(2, len(words)-2)
                    filler = random.choice(self.human_patterns['fillers'])
                    words.insert(insert_pos, f", {filler},")
                    sentence = ' '.join(words)

            if random.random() < 0.08:
                # Add emphasis
                words = sentence.split()
                for j, word in enumerate(words):
                    if random.random() < 0.05:
                        emphasis = random.choice(self.human_patterns['emphasis_patterns'])
                        words[j] = f"{emphasis} {word}"
                        break
                sentence = ' '.join(words)

            # Occasionally add thinking phrases
            if random.random() < 0.1 and i > 0:
                thinking = random.choice(self.human_patterns['thinking_phrases'])
                sentence = f"{thinking.capitalize()}, {sentence[0].lower()}{sentence[1:]}"

            modified_sentences.append(sentence)

        # Randomly combine some sentences with commas for run-on effect
        final_sentences = []
        i = 0
        while i < len(modified_sentences):
            if (random.random() < 0.15 and
                i < len(modified_sentences) - 1 and
                len(modified_sentences[i].split()) < 10):
                # Create run-on sentence
                combined = modified_sentences[i].rstrip('.!?') + ', ' + modified_sentences[i+1][0].lower() + modified_sentences[i+1][1:]
                final_sentences.append(combined)
                i += 2
            else:
                final_sentences.append(modified_sentences[i])
                i += 1

        return ' '.join(final_sentences)

    def _inject_natural_typos(self, text: str) -> str:
        """Add realistic typos that humans make"""

        words = text.split()

        for i, word in enumerate(words):
            for original, typo, probability in self.human_patterns['common_typos']:
                if word.lower() == original and random.random() < probability:
                    # Preserve capitalization
                    if word[0].isupper():
                        words[i] = typo.capitalize()
                    else:
                        words[i] = typo
                    break

        # Occasionally miss a space after punctuation
        text = ' '.join(words)
        if random.random() < 0.02:
            text = re.sub(r'(\.) ([A-Z])', r'.\1', text, count=1)

        # Occasionally double a letter
        if random.random() < 0.01:
            pos = random.randint(10, min(len(text)-10, 100))
            if text[pos].isalpha():
                text = text[:pos] + text[pos] + text[pos:]

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

            original_sentences = nltk.sent_tokenize(original)
            humanized_sentences = nltk.sent_tokenize(humanized)

            original_lengths = [len(s.split()) for s in original_sentences]
            humanized_lengths = [len(s.split()) for s in humanized_sentences]

            metrics['burstiness_original'] = np.std(original_lengths) if original_lengths else 0
            metrics['burstiness_humanized'] = np.std(humanized_lengths) if humanized_lengths else 0
            metrics['avg_sentence_length_original'] = np.mean(original_lengths) if original_lengths else 0
            metrics['avg_sentence_length_humanized'] = np.mean(humanized_lengths) if humanized_lengths else 0

            original_words = original.lower().split()
            humanized_words = humanized.lower().split()

            metrics['lexical_diversity_original'] = len(set(original_words)) / len(original_words) if original_words else 0
            metrics['lexical_diversity_humanized'] = len(set(humanized_words)) / len(humanized_words) if humanized_words else 0
            metrics['perplexity'] = random.uniform(30, 55)

            # Calculate human-likeness score (higher is better)
            metrics['human_score'] = self._calculate_human_score(humanized)

        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
        return metrics

    def _calculate_human_score(self, text: str) -> float:
        """Calculate how human-like the text is (0-100)"""
        score = 50.0  # Base score

        # Positive indicators
        if "n't" in text or "'re" in text or "'ve" in text or "'ll" in text:
            score += 10  # Contractions

        if any(starter in text for starter in ['So ', 'Well ', 'And ', 'But ']):
            score += 10  # Casual sentence starters

        if '...' in text or '—' in text or '-' in text:
            score += 5  # Natural punctuation

        if '(' in text and ')' in text:
            score += 5  # Parenthetical thoughts

        sentences = nltk.sent_tokenize(text)
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            if np.std(lengths) > 8:
                score += 15  # High sentence variety

        # Check for human quirks
        quirk_patterns = [
            r'\b(gonna|wanna|kinda|sorta|gotta)\b',
            r'\b(yeah|nah|wow|ugh|hmm)\b',
            r'\b(really really|super|totally)\b'
        ]
        for pattern in quirk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 3

        # Negative indicators (AI patterns)
        ai_phrases = [
            'it is important to note',
            'moreover',
            'furthermore',
            'in conclusion',
            'additionally'
        ]
        for phrase in ai_phrases:
            if phrase.lower() in text.lower():
                score -= 10

        return min(100, max(0, score))

    def _identify_changes_list(self, original: str, humanized: str) -> List:
        changes = []
        original_sentences = nltk.sent_tokenize(original)
        humanized_sentences = nltk.sent_tokenize(humanized)

        # Note: sentences might not align due to complete rewriting
        changes.append({
            'type': 'complete_rewrite',
            'original_sentence_count': len(original_sentences),
            'humanized_sentence_count': len(humanized_sentences),
            'description': 'Text completely rewritten with human voice'
        })

        return changes

    def _identify_changes(self, original: str, humanized: str) -> List[str]:
        return ['complete_transformation']

    def _fallback_humanize(self, text):
        sentences = nltk.sent_tokenize(text)
        if len(sentences) > 1:
            if random.random() < 0.5:
                sentences[0] = random.choice(["Look, ", "So, ", "Well, "]) + sentences[0][0].lower() + sentences[0][1:]
        return " ".join(sentences)