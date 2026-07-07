"""
高级文本分析服务

功能：
1. 关键词提取
2. 文本摘要
3. 情感详细分析
4. 文本统计信息
"""
from typing import Dict, List, Optional, Any
import re
from collections import Counter

from ..utils.logger import logger


class TextAnalysisService:
    """文本分析服务"""

    def __init__(self):
        self.stopwords = self._load_stopwords()

    def _load_stopwords(self) -> set:
        """加载停用词（简化版）"""
        # 常见中文和英文停用词
        stopwords = {
            # 中文
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
            # 英文
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "i", "you", "he", "she", "it", "we", "they",
        }
        return stopwords

    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10,
        language: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        提取关键词

        Args:
            text: 输入文本
            max_keywords: 最大关键词数量
            language: 语言 (auto/zh/en)

        Returns:
            关键词列表，包含词和权重
        """
        if language == "auto":
            language = self._detect_language(text)

        if language == "zh":
            return self._extract_keywords_chinese(text, max_keywords)
        else:
            return self._extract_keywords_english(text, max_keywords)

    def _detect_language(self, text: str) -> str:
        """检测文本语言"""
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        total_chars = len(text.strip())

        if total_chars == 0:
            return "en"

        chinese_ratio = chinese_chars / total_chars
        return "zh" if chinese_ratio > 0.3 else "en"

    def _extract_keywords_chinese(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """中文关键词提取（基于词频）"""
        # 简单的词频统计（2-4字词组）
        words = []

        # 提取2-4字词组
        for length in range(2, 5):
            for i in range(len(text) - length + 1):
                phrase = text[i:i+length]
                # 过滤包含非中文字符的词组
                if re.match(r'^[一-鿿]+$', phrase):
                    words.append(phrase)

        # 统计词频
        counter = Counter(words)

        # 过滤停用词和低频词
        keywords = []
        for word, count in counter.most_common(max_keywords * 2):
            if word in self.stopwords:
                continue
            if count < 2:
                continue
            keywords.append({
                "keyword": word,
                "weight": count,
                "frequency": count / len(words) if words else 0
            })

        return keywords[:max_keywords]

    def _extract_keywords_english(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """英文关键词提取（基于词频）"""
        # 分词并转小写
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        # 过滤停用词和短词
        words = [w for w in words if w not in self.stopwords and len(w) > 2]

        # 统计词频
        counter = Counter(words)

        # 提取关键词
        keywords = []
        for word, count in counter.most_common(max_keywords):
            keywords.append({
                "keyword": word,
                "weight": count,
                "frequency": count / len(words) if words else 0
            })

        return keywords

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        文本摘要（基于句子重要性）

        Args:
            text: 输入文本
            max_length: 最大摘要长度

        Returns:
            摘要文本
        """
        if len(text) <= max_length:
            return text

        # 简单实现：取前N个句子
        sentences = self._split_sentences(text)

        if not sentences:
            return text[:max_length] + "..."

        # 评分：首尾句子权重更高
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 1.0
            # 首尾句子加分
            if i == 0 or i == len(sentences) - 1:
                score *= 2
            # 句子长度加分（适中的长度更好）
            if 10 < len(sentence) < 100:
                score *= 1.5
            scored_sentences.append((score, sentence))

        # 按分数排序
        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        # 提取前几个句子组成摘要
        summary_sentences = []
        current_length = 0

        for score, sentence in scored_sentences:
            if current_length + len(sentence) > max_length:
                break
            summary_sentences.append(sentence)
            current_length += len(sentence)

        if not summary_sentences:
            return text[:max_length] + "..."

        return " ".join(summary_sentences) + ("..." if current_length < len(text) else "")

    def _split_sentences(self, text: str) -> List[str]:
        """分句（支持中英文）"""
        # 中英文分句符
        sentences = re.split(r'[。！？!?.]\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """
        获取文本统计信息

        Returns:
            统计信息字典
        """
        # 基本统计
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))

        # 单词/分词统计
        words_cn = len(re.findall(r'[一-鿿]', text))
        words_en = len(re.findall(r'\b[a-zA-Z]+\b', text))
        total_words = words_cn + words_en

        # 句子统计
        sentences = self._split_sentences(text)
        sentence_count = len(sentences)

        # 段落统计
        paragraphs = [p for p in text.split("\n") if p.strip()]
        paragraph_count = len(paragraphs)

        # 平均句长
        avg_sentence_length = char_count / sentence_count if sentence_count > 0 else 0

        # 语言检测
        language = self._detect_language(text)

        return {
            "char_count": char_count,
            "char_count_no_spaces": char_count_no_spaces,
            "word_count": total_words,
            "chinese_chars": words_cn,
            "english_words": words_en,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "language": language,
        }

    def analyze_sentiment_detail(self, text: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        详细情感分析

        Args:
            text: 输入文本
            result: 基础情感分析结果

        Returns:
            详细分析结果
        """
        # 基础结果
        label = result.get("label", "neutral")
        score = result.get("score", 0.5)

        # 提取关键词
        keywords = self.extract_keywords(text, max_keywords=5)

        # 文本摘要
        summary = self.summarize_text(text, max_length=100)

        # 文本统计
        stats = self.get_text_stats(text)

        # 情感强度
        if label == "positive":
            intensity = "强" if score > 0.8 else "中" if score > 0.6 else "弱"
        elif label == "negative":
            intensity = "强" if score > 0.8 else "中" if score > 0.6 else "弱"
        else:
            intensity = "中性"

        return {
            "label": label,
            "score": score,
            "intensity": intensity,
            "confidence": round(score, 4),
            "keywords": keywords,
            "summary": summary,
            "stats": stats,
        }


# 全局文本分析服务实例
text_analysis_service = TextAnalysisService()
