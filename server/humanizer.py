import re
import random
import hashlib
import json
import textstat
import nltk
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import spacy
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import torch

try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class HumanizationEngine:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.model.eval()

        self.tone_patterns = {
            'neutral': {
                'sentence_starters': ['', 'Additionally, ', 'Moreover, ', 'Furthermore, '],
                'connectors': ['and', 'but', 'however', 'therefore'],
                'intensifiers': []
            },
            'casual': {
                'sentence_starters': ['Well, ', 'So, ', 'You know, ', 'Actually, ', 'Honestly, '],
                'connectors': ['and', 'but', 'so', 'then', 'like'],
                'intensifiers': ['really', 'pretty', 'quite', 'super', 'totally'],
                'contractions': True
            },
            'formal': {
                'sentence_starters': ['', 'Furthermore, ', 'Additionally, ', 'Consequently, ', 'Subsequently, '],
                'connectors': ['and', 'however', 'therefore', 'moreover', 'nonetheless'],
                'intensifiers': [],
                'contractions': False
            },
            'persuasive': {
                'sentence_starters': ['Clearly, ', 'Obviously, ', 'Without doubt, ', 'It\'s evident that '],
                'connectors': ['and', 'but', 'therefore', 'thus', 'hence'],
                'intensifiers': ['absolutely', 'certainly', 'undoubtedly', 'definitely'],
            },
            'academic': {
                'sentence_starters': ['', 'Research indicates that ', 'Studies suggest that ', 'It has been observed that '],
                'connectors': ['and', 'however', 'furthermore', 'consequently', 'nevertheless'],
                'intensifiers': [],
                'contractions': False
            }
        }

        self.idioms = [
            "a piece of cake", "break the ice", "hit the nail on the head",
            "let the cat out of the bag", "once in a blue moon", "speak of the devil",
            "the ball is in your court", "under the weather", "wrap your head around",
            "cut to the chase", "get the ball rolling", "in a nutshell"
        ]

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
            torch.manual_seed(seed)

        preserved_elements = self._extract_preserved_elements(text, preserve_citations, preserve_quotes)

        processed_text = self._preprocess(text, preserved_elements)

        sentences = nltk.sent_tokenize(processed_text)
        humanized_sentences = []
        changes = []

        for i, sentence in enumerate(sentences):
            if self._should_preserve(sentence, preserved_elements):
                humanized_sentences.append(sentence)
                continue

            new_sentence = self._humanize_sentence(
                sentence,
                tone=tone,
                formality=formality,
                burstiness=burstiness,
                temperature=temperature,
                idiom_density=idiom_density,
                conciseness=conciseness,
                sentence_index=i,
                total_sentences=len(sentences)
            )

            if new_sentence != sentence:
                changes.append({
                    'original': sentence,
                    'humanized': new_sentence,
                    'position': i,
                    'changes_made': self._identify_changes(sentence, new_sentence)
                })

            humanized_sentences.append(new_sentence)

        humanized_text = ' '.join(humanized_sentences)

        humanized_text = self._restore_preserved_elements(humanized_text, preserved_elements)

        if integrity_mode == 'academic':
            humanized_text = self._apply_academic_integrity(humanized_text, preserved_elements)

        metrics = self._calculate_metrics(text, humanized_text)

        return {
            'humanized_text': humanized_text,
            'metrics': metrics,
            'changes': changes,
            'preserved_elements': preserved_elements
        }

    def _extract_preserved_elements(self, text: str, preserve_citations: bool, preserve_quotes: bool) -> Dict:
        elements = {'citations': [], 'quotes': []}

        if preserve_citations:
            citation_pattern = r'\([^)]*\d{4}[^)]*\)|\[[^\]]*\d+[^\]]*\]'
            citations = re.finditer(citation_pattern, text)
            for match in citations:
                elements['citations'].append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'placeholder': f'__CITATION_{len(elements["citations"])}__'
                })

        if preserve_quotes:
            quote_pattern = r'"[^"]+"|\'[^\']+\''
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

    def _should_preserve(self, sentence: str, preserved_elements: Dict) -> bool:
        for elements in preserved_elements.values():
            for element in elements:
                if element['placeholder'] in sentence:
                    return True
        return False

    def _humanize_sentence(
        self,
        sentence: str,
        tone: str,
        formality: float,
        burstiness: float,
        temperature: float,
        idiom_density: float,
        conciseness: float,
        sentence_index: int,
        total_sentences: int
    ) -> str:

        doc = self.nlp(sentence)

        humanized = sentence

        if random.random() < burstiness:
            sentence_length_variation = random.choice([-0.3, -0.2, 0, 0.2, 0.3])
            target_length = len(sentence.split()) * (1 + sentence_length_variation)
            humanized = self._adjust_sentence_length(humanized, target_length, conciseness)

        if tone in self.tone_patterns:
            pattern = self.tone_patterns[tone]

            if sentence_index == 0 or random.random() < 0.3:
                starter = random.choice(pattern['sentence_starters'])
                if starter and not humanized.startswith(starter):
                    humanized = starter + humanized[0].lower() + humanized[1:]

            if pattern.get('intensifiers') and random.random() < 0.2:
                humanized = self._add_intensifiers(humanized, pattern['intensifiers'])

            if pattern.get('contractions') is True and formality < 0.5:
                humanized = self._apply_contractions(humanized)
            elif pattern.get('contractions') is False:
                humanized = self._remove_contractions(humanized)

        if random.random() < idiom_density:
            humanized = self._insert_idiom(humanized)

        humanized = self._vary_vocabulary(humanized, temperature)

        humanized = self._adjust_formality(humanized, formality)

        return humanized

    def _adjust_sentence_length(self, sentence: str, target_length: float, conciseness: float) -> str:
        words = sentence.split()
        current_length = len(words)

        if conciseness > 0.7 and current_length > target_length:
            doc = self.nlp(sentence)
            non_essential = []
            for token in doc:
                if token.dep_ in ['advmod', 'amod'] and random.random() < 0.5:
                    non_essential.append(token.text)

            for word in non_essential[:int((current_length - target_length) / 2)]:
                words = [w for w in words if w != word]

        elif conciseness < 0.3 and current_length < target_length:
            descriptors = ['quite', 'rather', 'somewhat', 'particularly', 'especially']
            insert_positions = random.sample(range(len(words)), min(2, len(words)))
            for pos in sorted(insert_positions, reverse=True):
                words.insert(pos, random.choice(descriptors))

        return ' '.join(words)

    def _add_intensifiers(self, sentence: str, intensifiers: List[str]) -> str:
        doc = self.nlp(sentence)
        words = sentence.split()

        for token in doc:
            if token.pos_ in ['ADJ', 'ADV'] and random.random() < 0.3:
                intensifier = random.choice(intensifiers)
                idx = words.index(token.text)
                words.insert(idx, intensifier)
                break

        return ' '.join(words)

    def _apply_contractions(self, text: str) -> str:
        contractions = {
            'are not': "aren't",
            'cannot': "can't",
            'could not': "couldn't",
            'did not': "didn't",
            'do not': "don't",
            'does not': "doesn't",
            'had not': "hadn't",
            'has not': "hasn't",
            'have not': "haven't",
            'he is': "he's",
            'he will': "he'll",
            'he would': "he'd",
            'I am': "I'm",
            'I have': "I've",
            'I will': "I'll",
            'I would': "I'd",
            'is not': "isn't",
            'it is': "it's",
            'it will': "it'll",
            'she is': "she's",
            'she will': "she'll",
            'she would': "she'd",
            'should not': "shouldn't",
            'that is': "that's",
            'they are': "they're",
            'they have': "they've",
            'they will': "they'll",
            'was not': "wasn't",
            'we are': "we're",
            'we have': "we've",
            'we will': "we'll",
            'were not': "weren't",
            'what is': "what's",
            'will not': "won't",
            'would not': "wouldn't",
            'you are': "you're",
            'you have': "you've",
            'you will': "you'll"
        }

        result = text
        for full, contraction in contractions.items():
            result = re.sub(r'\b' + full + r'\b', contraction, result, flags=re.IGNORECASE)

        return result

    def _remove_contractions(self, text: str) -> str:
        expansions = {
            "aren't": 'are not',
            "can't": 'cannot',
            "couldn't": 'could not',
            "didn't": 'did not',
            "don't": 'do not',
            "doesn't": 'does not',
            "hadn't": 'had not',
            "hasn't": 'has not',
            "haven't": 'have not',
            "he's": 'he is',
            "he'll": 'he will',
            "he'd": 'he would',
            "I'm": 'I am',
            "I've": 'I have',
            "I'll": 'I will',
            "I'd": 'I would',
            "isn't": 'is not',
            "it's": 'it is',
            "it'll": 'it will',
            "she's": 'she is',
            "she'll": 'she will',
            "she'd": 'she would',
            "shouldn't": 'should not',
            "that's": 'that is',
            "they're": 'they are',
            "they've": 'they have',
            "they'll": 'they will',
            "wasn't": 'was not',
            "we're": 'we are',
            "we've": 'we have',
            "we'll": 'we will',
            "weren't": 'were not',
            "what's": 'what is',
            "won't": 'will not',
            "wouldn't": 'would not',
            "you're": 'you are',
            "you've": 'you have',
            "you'll": 'you will'
        }

        result = text
        for contraction, full in expansions.items():
            result = re.sub(r'\b' + contraction + r'\b', full, result, flags=re.IGNORECASE)

        return result

    def _insert_idiom(self, sentence: str) -> str:
        if len(sentence.split()) > 5 and random.random() < 0.3:
            idiom = random.choice(self.idioms)
            words = sentence.split()
            insert_pos = random.randint(1, len(words) - 1)
            words.insert(insert_pos, f", {idiom},")
            return ' '.join(words)
        return sentence

    def _vary_vocabulary(self, sentence: str, temperature: float) -> str:
        synonyms = {
            'good': ['great', 'excellent', 'fine', 'wonderful', 'positive'],
            'bad': ['poor', 'negative', 'unfortunate', 'problematic', 'difficult'],
            'very': ['quite', 'extremely', 'highly', 'particularly', 'especially'],
            'important': ['crucial', 'vital', 'essential', 'significant', 'key'],
            'show': ['demonstrate', 'illustrate', 'reveal', 'indicate', 'display'],
            'make': ['create', 'produce', 'generate', 'develop', 'form'],
            'use': ['utilize', 'employ', 'apply', 'implement', 'leverage']
        }

        words = sentence.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')
            if word_lower in synonyms and random.random() < temperature * 0.3:
                replacement = random.choice(synonyms[word_lower])
                if word[0].isupper():
                    replacement = replacement.capitalize()
                words[i] = word.replace(word_lower, replacement)

        return ' '.join(words)

    def _adjust_formality(self, sentence: str, formality: float) -> str:
        if formality > 0.7:
            informal_to_formal = {
                'kids': 'children',
                'stuff': 'materials',
                'things': 'items',
                'a lot': 'numerous',
                'get': 'obtain',
                'give': 'provide',
                'help': 'assist',
                'need': 'require',
                'want': 'desire',
                'think': 'believe'
            }
            for informal, formal in informal_to_formal.items():
                sentence = re.sub(r'\b' + informal + r'\b', formal, sentence, flags=re.IGNORECASE)

        elif formality < 0.3:
            formal_to_informal = {
                'children': 'kids',
                'obtain': 'get',
                'provide': 'give',
                'assist': 'help',
                'require': 'need',
                'numerous': 'a lot',
                'utilize': 'use',
                'commence': 'start',
                'terminate': 'end'
            }
            for formal, informal in formal_to_informal.items():
                sentence = re.sub(r'\b' + formal + r'\b', informal, sentence, flags=re.IGNORECASE)

        return sentence

    def _identify_changes(self, original: str, humanized: str) -> List[str]:
        changes = []

        if len(humanized) != len(original):
            changes.append('length_changed')

        if humanized.lower() != original.lower():
            changes.append('vocabulary_varied')

        if '"' in original and '"' not in humanized:
            changes.append('quotes_modified')

        return changes

    def _apply_academic_integrity(self, text: str, preserved_elements: Dict) -> str:
        watermark_hash = hashlib.sha256(text.encode()).hexdigest()[:8]

        zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        watermark_binary = ''.join(format(ord(c), '08b') for c in watermark_hash)

        words = text.split()
        watermark_idx = 0

        for i in range(0, len(words), 10):
            if watermark_idx < len(watermark_binary):
                if watermark_binary[watermark_idx] == '1':
                    words[i] += zero_width_chars[0]
                else:
                    words[i] += zero_width_chars[1]
                watermark_idx += 1

        return ' '.join(words)

    def _calculate_metrics(self, original: str, humanized: str) -> Dict:
        metrics = {}

        metrics['flesch_kincaid_original'] = textstat.flesch_kincaid_grade(original)
        metrics['flesch_kincaid_humanized'] = textstat.flesch_kincaid_grade(humanized)

        original_sentences = nltk.sent_tokenize(original)
        humanized_sentences = nltk.sent_tokenize(humanized)

        original_lengths = [len(s.split()) for s in original_sentences]
        humanized_lengths = [len(s.split()) for s in humanized_sentences]

        metrics['burstiness_original'] = np.std(original_lengths) if original_lengths else 0
        metrics['burstiness_humanized'] = np.std(humanized_lengths) if humanized_lengths else 0

        try:
            metrics['perplexity'] = self._calculate_perplexity(humanized)
        except:
            metrics['perplexity'] = 0

        metrics['avg_sentence_length_original'] = np.mean(original_lengths) if original_lengths else 0
        metrics['avg_sentence_length_humanized'] = np.mean(humanized_lengths) if humanized_lengths else 0

        metrics['lexical_diversity_original'] = len(set(original.lower().split())) / len(original.split()) if original else 0
        metrics['lexical_diversity_humanized'] = len(set(humanized.lower().split())) / len(humanized.split()) if humanized else 0

        return metrics

    def _calculate_perplexity(self, text: str) -> float:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            perplexity = torch.exp(loss)

        return perplexity.item()

def analyze_style(text: str) -> Dict:
    engine = HumanizationEngine()
    doc = engine.nlp(text)

    sentences = nltk.sent_tokenize(text)
    words = text.split()

    metrics = {
        'avg_sentence_length': np.mean([len(s.split()) for s in sentences]),
        'sentence_length_variance': np.std([len(s.split()) for s in sentences]),
        'lexical_diversity': len(set(words)) / len(words) if words else 0,
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
        'passive_voice_ratio': sum(1 for token in doc if token.dep_ == "nsubjpass") / len(doc),
        'adjective_ratio': sum(1 for token in doc if token.pos_ == "ADJ") / len(doc),
        'adverb_ratio': sum(1 for token in doc if token.pos_ == "ADV") / len(doc),
        'contraction_count': len(re.findall(r"'", text)),
        'formal_words': len([w for w in words if len(w) > 8]) / len(words) if words else 0
    }

    return metrics