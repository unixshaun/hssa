#!/usr/bin/env python

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinancialSentimentAnalyzer:
    """
    Multi-model sentiment analysis optimized for financial text
    """
    def __init__(self):
        # Primary: FinBERT (specifically trained on financial text)
        self.finbert_tokenizer = AutoTokenizer.from_pretrained(
            "ProsusAI/finbert"
        )
        self.finbert_model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )
        
        # Secondary: General BERT for cross-validation
        self.bert_tokenizer = AutoTokenizer.from_pretrained(
            "nlptown/bert-base-multilingual-uncased-sentiment"
        )
        self.bert_model = AutoModelForSequenceClassification.from_pretrained(
            "nlptown/bert-base-multilingual-uncased-sentiment"
        )
        
    def analyze_sentiment(self, text: str) -> dict:
        """
        Returns sentiment scores
        Output: {'label': 'positive'|'negative'|'neutral', 
                 'score': float, 'confidence': float}
        """
        # FinBERT analysis
        inputs = self.finbert_tokenizer(text, return_tensors="pt", 
                                       truncation=True, max_length=512)
        outputs = self.finbert_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Labels: [negative, neutral, positive]
        sentiment_idx = torch.argmax(probs).item()
        sentiment_labels = ['negative', 'neutral', 'positive']
        
        return {
            'label': sentiment_labels[sentiment_idx],
            'score': self.map_to_score(sentiment_idx),  # -1 to +1
            'confidence': probs[0][sentiment_idx].item(),
            'raw_probs': probs[0].tolist()
        }
    
    def map_to_score(self, label_idx: int) -> float:
        """Map categorical sentiment to continuous score"""
        mapping = {0: -1.0, 1: 0.0, 2: 1.0}
        return mapping[label_idx]
    
    def batch_analyze(self, texts: List[str]) -> List[dict]:
        """Efficient batch processing"""
        # Use GPU if available
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.finbert_model.to(device)
        
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
