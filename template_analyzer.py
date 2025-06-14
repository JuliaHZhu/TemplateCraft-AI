import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class EnglishTemplateAnalyzer:
    """英文模板分析器：拆解篇章结构和内容结构"""

    def __init__(self):
        # 定义英文连接词模式
        self.connective_patterns = {
            'causal': r'(because|since|as|so|therefore|thus|hence|consequently)',
            'contrast': r'(but|however|nevertheless|yet|nonetheless|whereas|while)',
            'addition': r'(and|also|moreover|furthermore|in addition|besides)',
            'comparison': r'(similarly|likewise|in the same way)',
            'example': r'(for example|for instance|such as|like|including)'
        }

        # 定义英文修辞模式
        self.rhetoric_patterns = {
            'simile': r'(like|as|resembles|similar to|comparable to)',
            'metaphor': r'(is|are|was|were) an? ([\w\s]+?) (of|for)',
            'parallelism': r'((.+?), ){2,}.+?(\.|;|:)',
            'rhetorical_question': r'(Who|What|Where|When|Why|How).*\?'
        }

    def analyze_discourse_structure(self, text: str) -> Dict[str, Any]:
        """分析篇章结构"""
        sentences = self._split_into_sentences(text)
        structure = {
            'sentence_count': len(sentences),
            'sentence_types': self._classify_sentences(sentences),
            'connectives': self._analyze_connectives(text),
            'rhetoric': self._analyze_rhetoric(text),
            'sentence_length': [len(s.split()) for s in sentences]
        }
        return structure

    def analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """分析内容结构"""
        concepts = self._extract_concepts(text)
        structure = {
            'core_concepts': concepts['core'],
            'related_concepts': concepts['related'],
            'argument_direction': self._analyze_argument_direction(text),
            'logical_flow': self._analyze_logical_flow(text)
        }
        return structure

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        sentences = re.split(r'[.!?]\s+', text)
        # 处理可能的末尾符号
        if sentences and sentences[-1] == '':
            sentences = sentences[:-1]
        return sentences

    def _classify_sentences(self, sentences: List[str]) -> Dict[str, int]:
        """分类句子类型（论点、论据、过渡、结论等）"""
        types = defaultdict(int)
        for s in sentences:
            if re.search(r'\b(argues|claims|contends|suggests|states)\b', s, re.IGNORECASE):
                types['thesis'] += 1  # 论点
            elif re.search(r'\b(for example|for instance|studies show|data indicates)\b', s, re.IGNORECASE):
                types['evidence'] += 1  # 论据
            elif re.search(r'\b(however|nevertheless|on the other hand)\b', s, re.IGNORECASE):
                types['transition'] += 1  # 过渡
            elif re.search(r'\b(in conclusion|therefore|thus|finally)\b', s, re.IGNORECASE):
                types['conclusion'] += 1  # 结论
            else:
                types['other'] += 1
        return types

    def _analyze_connectives(self, text: str) -> Dict[str, int]:
        """分析连接词使用情况"""
        result = defaultdict(int)
        for category, pattern in self.connective_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            result[category] += len(matches)
        return result

    def _analyze_rhetoric(self, text: str) -> Dict[str, int]:
        """分析修辞手法"""
        result = defaultdict(int)
        for category, pattern in self.rhetoric_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            result[category] += len(matches)
        return result

    def _extract_concepts(self, text: str) -> Dict[str, List[str]]:
        """提取核心概念和相关概念"""
        # 使用简单的词频统计
        words = re.findall(r'\b[A-Za-z]{3,}\b', text)
        word_freq = defaultdict(int)
        for word in words:
            word_lower = word.lower()
            word_freq[word_lower] += 1

        # 排序并提取核心和相关概念
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        core = [word for word, freq in sorted_words[:3]]
        related = [word for word, freq in sorted_words[3:8]]

        return {'core': core, 'related': related}

    def _analyze_argument_direction(self, text: str) -> Dict[str, Any]:
        """分析论述方向（正面/反面）"""
        positive_words = ['advantage', 'benefit', 'improvement', 'progress', 'success']
        negative_words = ['problem', 'challenge', 'issue', 'difficulty', 'failure']

        text_lower = text.lower()
        pos_count = sum(text_lower.count(word) for word in positive_words)
        neg_count = sum(text_lower.count(word) for word in negative_words)

        if pos_count > neg_count:
            direction = 'positive'
        elif neg_count > pos_count:
            direction = 'negative'
        else:
            direction = 'balanced'

        return {
            'positive': pos_count,
            'negative': neg_count,
            'direction': direction
        }

    def _analyze_logical_flow(self, text: str) -> str:
        """分析逻辑流程"""
        patterns = [
            (r'(problem|challenge).*(analysis|cause).*(solution|resolution)', 'problem-analysis-solution'),
            (r'(background|context).*(current situation|现状).*(future|prospect)', 'background-current-future'),
            (r'(claim|thesis).*(evidence|support).*(conclusion|restatement)', 'claim-evidence-conclusion')
        ]

        for pattern, flow in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return flow
        return 'other'

