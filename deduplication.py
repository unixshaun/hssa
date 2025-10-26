#!/usr/bin/env python

from hashlib import md5
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentDeduplicator:
    """
    Removes duplicate or near-duplicate content across platforms
    """
    def __init__(self):
        self.seen_hashes = set()
        self.vectorizer = TfidfVectorizer()
        self.recent_content = []  # Last 1000 items for fuzzy matching
        
    def is_duplicate(self, content: str, metadata: dict) -> bool:
        """Check if content is exact or near-duplicate"""
        # Exact match via hash
        content_hash = md5(content.encode()).hexdigest()
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        
        # Fuzzy match for cross-posts
        if len(self.recent_content) > 0:
            similarity = self.check_similarity(content)
            if similarity > 0.95:  # 95% similar = duplicate
                return True
        
        # Add to recent content buffer
        self.recent_content.append(content)
        if len(self.recent_content) > 1000:
            self.recent_content.pop(0)
        
        return False
    
    def check_similarity(self, new_content: str) -> float:
        """Calculate max similarity with recent content"""
        try:
            corpus = self.recent_content + [new_content]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            return float(similarities.max())
        except:
            return 0.0
