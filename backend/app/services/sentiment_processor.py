"""
Sentiment Processor
Pure sentiment analysis and text processing logic
"""
from typing import List
from pydantic import BaseModel
import re


class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    score: float  # -1.0 to 1.0
    label: str  # "positive" | "negative" | "neutral"
    confidence: float  # 0.0 to 1.0


class IntentResult(BaseModel):
    """Intent detection result"""
    intent: str  # "question" | "complaint" | "praise" | "neutral" | "spam"
    confidence: float


class CommentAnalysis(BaseModel):
    """Complete comment analysis"""
    text: str
    sentiment: SentimentResult
    intent: IntentResult
    language: str
    keywords: List[str]
    urgency_score: float  # 0.0 to 1.0
    requires_human: bool  # True if crisis or urgency > 0.8


class SentimentProcessor:
    """Service for sentiment analysis and text processing"""
    
    def __init__(self):
        # Positive/negative word lists for simple sentiment
        self.positive_words = {
            'love', 'great', 'awesome', 'excellent', 'amazing', 'perfect',
            'wonderful', 'fantastic', 'best', 'good', 'nice', 'beautiful',
            'thank', 'thanks', 'appreciate', 'helpful', 'impressed'
        }
        
        self.negative_words = {
            'hate', 'terrible', 'awful', 'horrible', 'worst', 'bad',
            'poor', 'disappointing', 'disappointed', 'angry', 'frustrated',
            'useless', 'waste', 'scam', 'fraud', 'never', 'refund'
        }
        
        self.question_words = {
            'how', 'what', 'when', 'where', 'why', 'who', 'which',
            'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does'
        }
        
        self.complaint_words = {
            'problem', 'issue', 'broken', 'not working', 'error', 'bug',
            'complaint', 'disappointed', 'refund', 'cancel', 'unsubscribe'
        }
        
        self.praise_words = {
            'love', 'amazing', 'excellent', 'perfect', 'best', 'thank',
            'appreciate', 'wonderful', 'fantastic', 'impressed'
        }
        
        self.spam_indicators = {
            'click here', 'buy now', 'limited time', 'act now', 'free money',
            'winner', 'congratulations', 'claim', 'prize', 'discount code'
        }
        
        self.urgent_words = {
            'urgent', 'emergency', 'asap', 'immediately', 'critical',
            'serious', 'help', 'please help', 'crisis', 'danger'
        }
    
    def analyze_comment(self, text: str) -> CommentAnalysis:
        """
        Analyze comment for sentiment, intent, and urgency
        
        Args:
            text: Comment text to analyze
            
        Returns:
            Complete comment analysis
        """
        text_lower = text.lower()
        
        # Sentiment analysis
        sentiment = self._calculate_sentiment(text_lower)
        
        # Intent detection
        intent = self._detect_intent(text_lower)
        
        # Language detection (simple)
        language = self._detect_language(text)
        
        # Extract keywords
        keywords = self._extract_keywords(text_lower)
        
        # Calculate urgency
        urgency_score = self._calculate_urgency(text_lower)
        
        # Determine if human review needed
        requires_human = (
            urgency_score > 0.8 or
            sentiment.score < -0.7 or
            intent.intent == "complaint"
        )
        
        return CommentAnalysis(
            text=text,
            sentiment=sentiment,
            intent=intent,
            language=language,
            keywords=keywords,
            urgency_score=urgency_score,
            requires_human=requires_human
        )
    
    def _calculate_sentiment(self, text: str) -> SentimentResult:
        """Calculate sentiment score"""
        words = set(text.split())
        
        positive_count = len(words & self.positive_words)
        negative_count = len(words & self.negative_words)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return SentimentResult(
                score=0.0,
                label="neutral",
                confidence=0.5
            )
        
        # Calculate score
        score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine label
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        
        # Confidence based on number of sentiment words
        confidence = min(total_sentiment_words / 5.0, 1.0)
        
        return SentimentResult(
            score=round(score, 2),
            label=label,
            confidence=round(confidence, 2)
        )
    
    def _detect_intent(self, text: str) -> IntentResult:
        """Detect comment intent"""
        words = set(text.split())
        
        # Check for spam
        spam_score = sum(1 for indicator in self.spam_indicators if indicator in text)
        if spam_score >= 2:
            return IntentResult(intent="spam", confidence=0.9)
        
        # Check for question
        has_question_mark = '?' in text
        question_word_count = len(words & self.question_words)
        if has_question_mark or question_word_count >= 2:
            return IntentResult(intent="question", confidence=0.8)
        
        # Check for complaint
        complaint_score = len(words & self.complaint_words)
        if complaint_score >= 2:
            return IntentResult(intent="complaint", confidence=0.85)
        
        # Check for praise
        praise_score = len(words & self.praise_words)
        if praise_score >= 2:
            return IntentResult(intent="praise", confidence=0.8)
        
        # Default to neutral
        return IntentResult(intent="neutral", confidence=0.6)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Very basic - just check for common Spanish words
        spanish_words = {'hola', 'gracias', 'por favor', 'buenos', 'días'}
        words = set(text.lower().split())
        
        if len(words & spanish_words) > 0:
            return "es"
        
        return "en"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are'
        }
        
        # Clean and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter and get unique keywords
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top 5 most relevant
        return list(set(keywords))[:5]
    
    def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency score"""
        words = set(text.split())
        
        urgent_count = len(words & self.urgent_words)
        has_exclamation = text.count('!') >= 2
        has_caps = sum(1 for c in text if c.isupper()) > len(text) * 0.5
        
        urgency = 0.0
        
        if urgent_count > 0:
            urgency += 0.4
        if has_exclamation:
            urgency += 0.3
        if has_caps:
            urgency += 0.3
        
        return min(urgency, 1.0)


# Global instance
sentiment_processor = SentimentProcessor()
