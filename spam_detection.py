#!/usr/bin/env python
import re
from datetime import datetime, timedelta

class SpamBotFilter:
    """
    Filters out spam, bots, and low-quality content
    """
    def __init__(self):
        self.spam_patterns = [
            r'(click here|buy now|limited time)',
            r'(🚀){3,}',  # Excessive rocket emojis
            r'(!!!){2,}',  # Excessive punctuation
            r'(dm me|contact me|join my)',  # Solicitation
        ]
        self.known_bots = set()  # Load from database
        self.user_post_history = {}  # Track posting patterns
        
    def is_spam(self, content: str, metadata: dict) -> bool:
        """Determine if content is spam"""
        # Check content patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, content.lower()):
                return True
        
        # Check for known bot accounts
        if metadata.get('author') in self.known_bots:
            return True
        
        # Check posting velocity (bot detection)
        author = metadata.get('author')
        if self.is_posting_too_fast(author):
            return True
        
        # Check content quality (very short, no tickers mentioned, etc.)
        if len(content) < 20 and not self.contains_financial_terms(content):
            return True
        
        return False
    
    def is_posting_too_fast(self, author: str) -> bool:
        """Detect bot-like posting patterns"""
        if author not in self.user_post_history:
            self.user_post_history[author] = []
        
        now = datetime.now()
        self.user_post_history[author].append(now)
        
        # Remove posts older than 1 hour
        self.user_post_history[author] = [
            ts for ts in self.user_post_history[author]
            if ts > now - timedelta(hours=1)
        ]
        
        # Flag if >50 posts per hour
        return len(self.user_post_history[author]) > 50
    
    def contains_financial_terms(self, text: str) -> bool:
        """Check if text contains financial terminology"""
        financial_terms = ['stock', 'ticker', 'calls', 'puts', 'buy', 
                          'sell', 'dd', 'analysis', 'target', 'price']
        text_lower = text.lower()
        return any(term in text_lower for term in financial_terms)
