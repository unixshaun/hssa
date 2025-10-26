#!/usr/bin/env python
import praw
from datetime import datetime, timedelta

class RedditSentimentScraper:
    """
    Custom Reddit scraper for financial subreddits
    Uses official PRAW (Python Reddit API Wrapper)
    """
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='HedgeFundSentiment/1.0'
        )
        self.target_subs = [
            'wallstreetbets', 'stocks', 'investing', 
            'options', 'SecurityAnalysis'
        ]
        
    def stream_submissions(self, subreddit_name: str):
        """Real-time stream of new submissions"""
        subreddit = self.reddit.subreddit(subreddit_name)
        for submission in subreddit.stream.submissions(skip_existing=True):
            yield {
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': submission.created_utc,
                'author': str(submission.author),
                'url': submission.url,
                'subreddit': subreddit_name
            }
    
    def get_hot_posts(self, subreddit_name: str, limit=100):
        """Batch fetch hot posts"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for submission in subreddit.hot(limit=limit):
            posts.append({
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'upvote_ratio': submission.upvote_ratio,
                'created_utc': submission.created_utc
            })
        return posts
    
    def get_ticker_mentions(self, text: str) -> list:
        """Extract ticker symbols from text"""
        # Regex for $TICKER or known tickers
        import re
        cashtags = re.findall(r'\$[A-Z]{1,5}\b', text)
        # Also check against known ticker list
        return [tag.replace('$', '') for tag in cashtags]
