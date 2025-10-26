#!/usr/bin/env python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """
    Enforces rate limits to respect platform ToS
    """
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        
    async def wait_if_needed(self):
        """Block if rate limit would be exceeded"""
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls = [c for c in self.calls if c > now - timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            # Wait until oldest call expires
            wait_time = 60 - (now - self.calls[0]).seconds
            await asyncio.sleep(wait_time)
            
        self.calls.append(now)
