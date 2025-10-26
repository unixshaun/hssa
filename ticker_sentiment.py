#!/usr/bin/env python

import pandas as pd
from collections import defaultdict

class TickerSentimentAggregator:
    """
    Aggregates sentiment scores per ticker across all sources
    """
    def __init__(self):
        self.platform_weights = {
            'licensed_twitter': 0.30,    # SMA data
            'licensed_news': 0.25,       # RavenPack
            'reddit': 0.20,
            'discord': 0.15,
            'telegram': 0.10,
        }
    
    def calculate_ticker_sentiment(self, ticker: str, data: pd.DataFrame) -> dict:
        """
        Calculate comprehensive sentiment for a specific ticker
        Returns: {
            'overall_score': float,
            'volume': int,
            'momentum': float,
            'platform_breakdown': dict,
            'unusual_activity': bool
        }
        """
        ticker_data = data[data['tickers'].str.contains(ticker, na=False)]
        
        if len(ticker_data) == 0:
            return None
        
        # Weighted sentiment by platform
        platform_sentiments = {}
        for platform, weight in self.platform_weights.items():
            platform_data = ticker_data[ticker_data['platform'] == platform]
            if len(platform_data) > 0:
                avg_sentiment = platform_data['sentiment_score'].mean()
                platform_sentiments[platform] = avg_sentiment
        
        # Overall weighted score
        overall_score = sum(
            sentiment * self.platform_weights[platform]
            for platform, sentiment in platform_sentiments.items()
        )
        
        # Normalize if not all platforms present
        total_weight = sum(
            self.platform_weights[p] for p in platform_sentiments.keys()
        )
        overall_score = overall_score / total_weight if total_weight > 0 else 0
        
        # Calculate momentum
        momentum = self.calculate_ticker_momentum(ticker, data)
        
        # Detect unusual activity
        unusual = self.detect_unusual_activity(ticker, ticker_data)
        
        return {
            'ticker': ticker,
            'overall_score': round(overall_score, 3),
            'volume': len(ticker_data),
            'momentum': round(momentum, 3),
            'platform_breakdown': platform_sentiments,
            'unusual_activity': unusual,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_ticker_momentum(self, ticker: str, data: pd.DataFrame) -> float:
        """Calculate sentiment momentum for ticker"""
        now = datetime.now()
        ticker_data = data[data['tickers'].str.contains(ticker, na=False)]
        
        # Last 4 hours split into 4 buckets
        buckets = []
        for i in range(4):
            start = now - timedelta(hours=4-i)
            end = now - timedelta(hours=3-i)
            bucket_data = ticker_data[
                (ticker_data['timestamp'] > start) &
                (ticker_data['timestamp'] <= end)
            ]
            if len(bucket_data) > 0:
                buckets.append(bucket_data['sentiment_score'].mean())
            else:
                buckets.append(None)
        
        # Calculate trend
        valid_buckets = [b for b in buckets if b is not None]
        if len(valid_buckets) < 2:
            return 0.0
        
        # Simple linear trend
        momentum = valid_buckets[-1] - valid_buckets[0]
        return max(min(momentum, 1.0), -1.0)
    
    def detect_unusual_activity(self, ticker: str, ticker_data: pd.DataFrame) -> bool:
        """Flag unusual spikes in volume or sentiment"""
        now = datetime.now()
        last_hour = ticker_data[ticker_data['timestamp'] > now - timedelta(hours=1)]
        
        # Compare to 7-day baseline
        week_ago = now - timedelta(days=7)
        historical = ticker_data[ticker_data['timestamp'] > week_ago]
        
        if len(historical) == 0:
            return False
        
        # Volume spike detection
        current_volume = len(last_hour)
        avg_volume = len(historical) / (7 * 24)  # Per hour average
        volume_spike = current_volume > (avg_volume * 3)  # 3x baseline
        
        # Sentiment divergence detection
        current_sentiment = last_hour['sentiment_score'].mean()
        avg_sentiment = historical['sentiment_score'].mean()
        sentiment_divergence = abs(current_sentiment - avg_sentiment) > 0.5
        
        return volume_spike or sentiment_divergence
