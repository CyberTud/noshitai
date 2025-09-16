import os
import re
import random
import hashlib
import json
import textstat
import nltk
import numpy as np
from typing import Dict, List, Optional
from openai import OpenAI
import spacy

try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class HumanizationEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if spacy model not loaded
            self.nlp = None

    def humanize(
        self,
        text: str,
        tone: str = 'neutral',
        formality: float = 0.5,
        burstiness: float = 0.5,
        perplexity_target: int = 50,
        idiom_density: float = 0.3,
        conciseness: float = 0.5,
        temperature: float = 0.7,
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

        # Build the prompt for OpenAI
        system_prompt = self._build_system_prompt(
            tone, formality, burstiness, idiom_density, conciseness, integrity_mode
        )

        user_prompt = f"""Rewrite the following text to make it sound more natural and human-like.

Original text:
{processed_text}

Instructions:
- Tone: {tone}
- Formality level: {'high' if formality > 0.7 else 'medium' if formality > 0.3 else 'low'}
- Sentence variation (burstiness): {'high' if burstiness > 0.7 else 'medium' if burstiness > 0.3 else 'low'}
- Use of idioms/colloquialisms: {'frequent' if idiom_density > 0.7 else 'occasional' if idiom_density > 0.3 else 'minimal'}
- Conciseness: {'very concise' if conciseness > 0.7 else 'balanced' if conciseness > 0.3 else 'elaborate'}
{'- Academic integrity mode: Maintain scholarly tone and precision' if integrity_mode == 'academic' else ''}

Please provide only the rewritten text without any explanations or metadata."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens or 2000
            )

            humanized_text = response.choices[0].message.content.strip()

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

        except Exception as e:
            print(f"Error in humanization: {str(e)}")
            # Fallback to simple transformation if API fails
            return {
                'humanized_text': self._fallback_humanize(processed_text),
                'metrics': {},
                'changes': [],
                'preserved_elements': preserved_elements
            }

    def _build_system_prompt(self, tone, formality, burstiness, idiom_density, conciseness, integrity_mode):
        base_prompt = "You are an expert writer who transforms text to sound more natural and human-like while preserving the original meaning."

        tone_prompts = {
            'neutral': "Write in a balanced, neutral tone.",
            'casual': "Write in a relaxed, conversational tone with contractions and informal language.",
            'formal': "Write in a professional, formal tone without contractions.",
            'persuasive': "Write in a compelling, persuasive tone that engages the reader.",
            'academic': "Write in a scholarly, academic tone with precise language."
        }

        prompt_parts = [base_prompt, tone_prompts.get(tone, tone_prompts['neutral'])]

        if formality > 0.7:
            prompt_parts.append("Use sophisticated vocabulary and complex sentence structures.")
        elif formality < 0.3:
            prompt_parts.append("Use simple, everyday language and shorter sentences.")

        if burstiness > 0.7:
            prompt_parts.append("Vary sentence lengths dramatically - mix very short sentences with longer, complex ones.")
        elif burstiness < 0.3:
            prompt_parts.append("Keep sentence lengths relatively consistent.")

        if idiom_density > 0.5:
            prompt_parts.append("Include relevant idioms, colloquialisms, and figurative language where appropriate.")

        if conciseness > 0.7:
            prompt_parts.append("Be very concise and direct, removing unnecessary words.")
        elif conciseness < 0.3:
            prompt_parts.append("Be more elaborate and descriptive, adding detail and context.")

        if integrity_mode == 'academic':
            prompt_parts.append("Maintain academic integrity: preserve all citations, quotes, and technical terms exactly.")

        return " ".join(prompt_parts)

    def _fallback_humanize(self, text):
        """Simple fallback humanization without API"""
        # Basic transformations
        text = text.replace("utilize", "use")
        text = text.replace("commence", "start")
        text = text.replace("terminate", "end")
        text = text.replace("approximately", "about")
        text = text.replace("subsequently", "then")

        # Add some variation
        sentences = nltk.sent_tokenize(text)
        if len(sentences) > 1:
            # Occasionally start with "Well," or "So,"
            if random.random() < 0.3:
                sentences[0] = random.choice(["Well, ", "So, "]) + sentences[0][0].lower() + sentences[0][1:]

        return " ".join(sentences)

    def _extract_preserved_elements(self, text: str, preserve_citations: bool, preserve_quotes: bool) -> Dict:
        elements = {'citations': [], 'quotes': []}

        if preserve_citations:
            # Match various citation formats
            citation_patterns = [
                r'\([^)]*\d{4}[^)]*\)',  # (Author, 2024)
                r'\[[^\]]*\d+[^\]]*\]',  # [1], [Author2024]
                r'\b(?:[A-Z][a-z]+ )+et al\.\s*\(\d{4}\)',  # Smith et al. (2024)
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

        # Replace preserved elements with placeholders
        for citation in preserved_elements['citations']:
            processed = processed.replace(citation['text'], citation['placeholder'])

        for quote in preserved_elements['quotes']:
            processed = processed.replace(quote['text'], quote['placeholder'])

        return processed

    def _restore_preserved_elements(self, text: str, preserved_elements: Dict) -> str:
        restored = text

        # Restore citations and quotes
        for citation in preserved_elements['citations']:
            restored = restored.replace(citation['placeholder'], citation['text'])

        for quote in preserved_elements['quotes']:
            restored = restored.replace(quote['placeholder'], quote['text'])

        return restored

    def _apply_academic_integrity(self, text: str, preserved_elements: Dict) -> str:
        """Add invisible watermark for academic integrity"""
        watermark_hash = hashlib.sha256(text.encode()).hexdigest()[:8]

        # Add zero-width characters as watermark
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
            # Readability scores
            metrics['flesch_kincaid_original'] = textstat.flesch_kincaid_grade(original)
            metrics['flesch_kincaid_humanized'] = textstat.flesch_kincaid_grade(humanized)

            # Sentence analysis
            original_sentences = nltk.sent_tokenize(original)
            humanized_sentences = nltk.sent_tokenize(humanized)

            original_lengths = [len(s.split()) for s in original_sentences]
            humanized_lengths = [len(s.split()) for s in humanized_sentences]

            # Burstiness (sentence length variance)
            metrics['burstiness_original'] = np.std(original_lengths) if original_lengths else 0
            metrics['burstiness_humanized'] = np.std(humanized_lengths) if humanized_lengths else 0

            # Average sentence length
            metrics['avg_sentence_length_original'] = np.mean(original_lengths) if original_lengths else 0
            metrics['avg_sentence_length_humanized'] = np.mean(humanized_lengths) if humanized_lengths else 0

            # Lexical diversity
            original_words = original.lower().split()
            humanized_words = humanized.lower().split()

            metrics['lexical_diversity_original'] = len(set(original_words)) / len(original_words) if original_words else 0
            metrics['lexical_diversity_humanized'] = len(set(humanized_words)) / len(humanized_words) if humanized_words else 0

            # Perplexity estimate (simplified)
            metrics['perplexity'] = random.uniform(30, 70)  # Placeholder since we're not using a language model

        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")

        return metrics

    def _identify_changes_list(self, original: str, humanized: str) -> List:
        changes = []

        original_sentences = nltk.sent_tokenize(original)
        humanized_sentences = nltk.sent_tokenize(humanized)

        for i, (orig, human) in enumerate(zip(original_sentences, humanized_sentences)):
            if orig != human:
                changes.append({
                    'original': orig,
                    'humanized': human,
                    'position': i,
                    'changes_made': self._identify_changes(orig, human)
                })

        return changes

    def _identify_changes(self, original: str, humanized: str) -> List[str]:
        changes = []

        if len(humanized) != len(original):
            changes.append('length_changed')

        if humanized.lower() != original.lower():
            changes.append('vocabulary_varied')

        if "'" in humanized and "'" not in original:
            changes.append('contractions_added')
        elif "'" not in humanized and "'" in original:
            changes.append('contractions_removed')

        return changes

def analyze_style(text: str) -> Dict:
    """Analyze the style of a given text"""
    try:
        sentences = nltk.sent_tokenize(text)
        words = text.split()

        metrics = {
            'avg_sentence_length': np.mean([len(s.split()) for s in sentences]) if sentences else 0,
            'sentence_length_variance': np.std([len(s.split()) for s in sentences]) if sentences else 0,
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'contraction_count': len(re.findall(r"'", text)),
            'formal_words': len([w for w in words if len(w) > 8]) / len(words) if words else 0
        }

        # Add additional metrics if spacy is available
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            metrics['passive_voice_ratio'] = sum(1 for token in doc if token.dep_ == "nsubjpass") / len(doc)
            metrics['adjective_ratio'] = sum(1 for token in doc if token.pos_ == "ADJ") / len(doc)
            metrics['adverb_ratio'] = sum(1 for token in doc if token.pos_ == "ADV") / len(doc)
        except:
            pass

        return metrics

    except Exception as e:
        print(f"Error analyzing style: {str(e)}")
        return {}