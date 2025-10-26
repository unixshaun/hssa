#!/usr/bin/env python

indices.py
import pandas as pd
from datetime import datetime, timedelta

class FearGreedIndex:
    """
    Constructs a custom Fear & Greed index from sentiment data
    Range: 0 (Extreme Fear) to 100 (Extreme Greed)
    """
    def __init__(self):
        self.weights = {
            'sentiment_score': 0.35,      # Aggregate sentiment
            'volume': 0.25,               # Discussion volume (vs baseline)
            'momentum': 0.20,             # Rate of change
            'put_call_mentions': 0.10,    # Options sentiment
            'volatility_mentions': 0.10,  # Fear keywords
        }
        
    def calculate(self, data: pd.DataFrame, window='1H') -> float:
        """
        Calculate current fear/greed index value
        Input: DataFrame with columns [timestamp, sentiment, ticker, platform]
        """
        now = datetime.now()
        recent_data = data[data['timestamp'] > now - timedelta(hours=1)]
        
        if len(recent_data) == 0:
            return 50.0  # Neutral if no data
        
        # Component 1: Average Sentiment (-1 to +1 → 0 to 100)
        avg_sentiment = recent_data['sentiment_score'].mean()
        sentiment_component = (avg_sentiment + 1) * 50  # Scale to 0-100
        
        # Component 2: Volume vs Baseline
        current_volume = len(recent_data)
        baseline_volume = self.get_baseline_volume(data, window)
        volume_ratio = current_volume / baseline_volume if baseline_volume > 0 else 1.0
        volume_component = min(volume_ratio * 50, 100)  # Cap at 100
        
        # Component 3: Momentum (sentiment change rate)
        momentum = self.calculate_momentum(data)
        momentum_component = (momentum + 1) * 50
        
        # Component 4: Put/Call Sentiment
        put_call_component = self.analyze_options_sentiment(recent_data)
        
        # Component 5: Volatility/Fear Keywords
        volatility_component = self.analyze_fear_keywords(recent_data)
        
        # Weighted average
        index_value = (
            sentiment_component * self.weights['sentiment_score'] +
            volume_component * self.weights['volume'] +
            momentum_component * self.weights['momentum'] +
            put_call_component * self.weights['put_call_mentions'] +
            volatility_component * self.weights['volatility_mentions']
        )
        
        return round(index_value, 2)
    
    def get_baseline_volume(self, data: pd.DataFrame, window: str) -> float:
        """Calculate baseline volume (7-day average)"""
        week_ago = datetime.now() - timedelta(days=7)
        historical = data[data['timestamp'] > week_ago]
        
        # Posts per hour average
        return len(historical) / (7 * 24)
    
    def calculate_momentum(self, data: pd.DataFrame) -> float:
        """Calculate sentiment momentum (-1 to +1)"""
        now = datetime.now()
        
        # Compare last hour vs previous hour
        last_hour = data[data['timestamp'] > now - timedelta(hours=1)]
        prev_hour = data[
            (data['timestamp'] > now - timedelta(hours=2)) &
            (data['timestamp'] <= now - timedelta(hours=1))
        ]
        
        if len(prev_hour) == 0:
            return 0.0
        
        last_sentiment = last_hour['sentiment_score'].mean()
        prev_sentiment = prev_hour['sentiment_score'].mean()
        
        # Normalized change
        change = last_sentiment - prev_sentiment
        return max(min(change, 1.0), -1.0)  # Clamp to [-1, 1]
    
    def analyze_options_sentiment(self, data: pd.DataFrame) -> float:
        """Analyze put/call mentions (0-100 scale)"""
        put_keywords = ['put', 'puts', 'puts']
        call_keywords = ['call', 'calls', 'calls']
        
        data['content_lower'] = data['content'].str.lower()
        
        put_count = data['content_lower'].str.contains('|'.join(put_keywords)).sum()
        call_count = data['content_lower'].str.contains('|'.join(call_keywords)).sum()
        
        if put_count + call_count == 0:
            return 50.0  # Neutral
        
        # More calls = greedy, more puts = fearful
        call_ratio = call_count / (put_count + call_count)
        return call_ratio * 100
    
    def analyze_fear_keywords(self, data: pd.DataFrame) -> float:
        """Analyze fear/greed keywords (0-100 scale)"""
        fear_keywords = ['crash', 'tank', 'dump', 'fear', 'panic', 'sell', 'bearish']
        greed_keywords = ['moon', 'rocket', 'bull', 'rally', 'buy', 'lambo', 'breakout']
        
        data['content_lower'] = data['content'].str.lower()
        
        fear_mentions = sum(
            data['content_lower'].str.contains(kw).sum() 
            for kw in fear_keywords
        )
        greed_mentions = sum(
            data['content_lower'].str.contains(kw).sum() 
            for kw in greed_keywords
        )
        
        total = fear_mentions + greed_mentions
        if total == 0:
            return 50.0
        
        greed_ratio = greed_mentions / total
        return greed_ratio * 100
    
    def get_interpretation(self, index_value: float) -> str:
        """Human-readable interpretation"""
        if index_value >= 80:
            return "Extreme Greed"
        elif index_value >= 60:
            return "Greed"
        elif index_value >= 40:
            return "Neutral"
        elif index_value >= 20:
            return "Fear"
        else:
            return "Extreme Fear"
