#!/usr/bin/env python
import re
from typing import List, Set

class TickerExtractor:
    """
    Extracts stock tickers from unstructured text
    Handles: $CASHTAGS, company names, common misspellings
    """
    def __init__(self):
        # Load ticker reference database
        self.known_tickers = self.load_ticker_database()
        self.company_to_ticker = self.load_company_mappings()
        
    def extract_tickers(self, text: str) -> Set[str]:
        """Extract all valid tickers from text"""
        tickers = set()
        
        # Method 1: Cashtags ($AAPL)
        cashtags = re.findall(r'\$([A-Z]{1,5})\b', text)
        tickers.update(t for t in cashtags if t in self.known_tickers)
        
        # Method 2: Standalone uppercase words (context-aware)
        words = re.findall(r'\b([A-Z]{1,5})\b', text)
        for word in words:
            if word in self.known_tickers and self.is_ticker_context(text, word):
                tickers.add(word)
        
        # Method 3: Company name matching
        text_lower = text.lower()
        for company, ticker in self.company_to_ticker.items():
            if company in text_lower:
                tickers.add(ticker)
        
        return tickers
    
    def is_ticker_context(self, text: str, word: str) -> bool:
        """Determine if uppercase word is likely a ticker vs acronym"""
        # Check for financial context words nearby
        context_words = ['stock', 'shares', 'calls', 'puts', 'long', 'short', 
                        'buy', 'sell', 'price', 'target', 'dd', 'yolo']
        text_lower = text.lower()
        return any(cw in text_lower for cw in context_words)
    
    def load_ticker_database(self) -> Set[str]:
        """Load valid ticker symbols"""
        # In production: load from database or file
        # Include NYSE, NASDAQ, major international exchanges
        return {'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMC', 'GME', ...}
    
    def load_company_mappings(self) -> dict:
        """Map company names to tickers"""
        return {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'tesla': 'TSLA',
            'gamestop': 'GME',
            ...
        }
