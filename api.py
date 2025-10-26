#!/usr/bin/env python

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI(title="Hedge Fund Sentiment API")

class SentimentAPI:
    """
    REST API for accessing sentiment data
    """
    
    @app.get("/api/v1/fear-greed")
    async def get_fear_greed_index(self, historical: bool = False):
        """
        Get current or historical Fear & Greed Index
        """
        if historical:
            # Return last 30 days
            query = """
                SELECT timestamp, index_value, interpretation
                FROM fear_greed_index
                WHERE timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
            """
            data = await self.db.fetch(query)
            return {"data": data}
        else:
            # Return current value
            query = """
                SELECT index_value, interpretation, components
                FROM fear_greed_index
                ORDER BY timestamp DESC
                LIMIT 1
            """
            current = await self.db.fetchrow(query)
            return {
                "current_value": current['index_value'],
                "interpretation": current['interpretation'],
                "components": current['components'],
                "as_of": datetime.now().isoformat()
            }
    
    @app.get("/api/v1/ticker/{ticker}/sentiment")
    async def get_ticker_sentiment(self, ticker: str, hours: int = 24):
        """
        Get sentiment data for specific ticker
        """
        query = """
            SELECT 
                time_bucket('1 hour', timestamp) AS hour,
                AVG(sentiment_score) AS avg_sentiment,
                COUNT(*) AS volume,
                MAX(sentiment_score) AS max_sentiment,
                MIN(sentiment_score) AS min_sentiment
            FROM sentiment_data
            WHERE $1 = ANY(tickers)
                AND timestamp > NOW() - INTERVAL '%s hours'
                AND is_spam = FALSE
            GROUP BY hour
            ORDER BY hour DESC
        """ % hours
        
        data = await self.db.fetch(query, ticker)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data for ticker {ticker}")
        
        return {
            "ticker": ticker,
            "timeframe_hours": hours,
            "data": data
        }
    
    @app.get("/api/v1/tickers/trending")
    async def get_trending_tickers(self, limit: int = 20):
        """
        Get most mentioned tickers in last 24 hours
        """
        query = """
            SELECT 
                unnest(tickers) AS ticker,
                COUNT(*) AS mentions,
                AVG(sentiment_score) AS avg_sentiment
            FROM sentiment_data
            WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND is_spam = FALSE
            GROUP BY ticker
            ORDER BY mentions DESC
            LIMIT $1
        """
        
        data = await self.db.fetch(query, limit)
        return {"trending_tickers": data}
    
    @app.get("/api/v1/unusual-activity")
    async def get_unusual_activity(self, hours: int = 24):
        """
        Get tickers with unusual activity
        """
        query = """
            SELECT ticker, alert_type, severity, details, timestamp
            FROM unusual_activity_log
            WHERE timestamp > NOW() - INTERVAL '%s hours'
                AND severity IN ('medium', 'high')
            ORDER BY timestamp DESC
        """ % hours
        
        alerts = await self.db.fetch(query)
        return {"unusual_activity": alerts}
    
    @app.websocket("/ws/sentiment-stream")
    async def sentiment_stream(self, websocket):
        """
        WebSocket endpoint for real-time sentiment stream
        """
        await websocket.accept()
        
        try:
            while True:
                # Stream new sentiment data as it arrives
                new_data = await self.get_latest_sentiment()
                await websocket.send_json(new_data)
                await asyncio.sleep(1)  # 1 second updates
        except:
            await websocket.close()
    
    async def get_latest_sentiment(self):
        """Fetch latest sentiment data"""
        query = """
            SELECT * FROM sentiment_data
            WHERE timestamp > NOW() - INTERVAL '10 seconds'
            ORDER BY timestamp DESC
        """
        return await self.db.fetch(query)

# Authentication middleware (simplified)
def verify_api_key(api_key: str):
    """Verify API key for internal fund access"""
    valid_keys = os.getenv('API_KEYS', '').split(',')
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True
