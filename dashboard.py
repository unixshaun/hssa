#!/usr/bin/env python

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

class SentimentDashboard:
    """
    Internal dashboard for analysts and PMs
    """
    def __init__(self):
        st.set_page_config(page_title="Sentiment Analysis Dashboard", 
                          layout="wide")
    
    def run(self):
        """Main dashboard loop"""
        st.title("🎯 Hedge Fund Sentiment Analysis")
        
        # Sidebar filters
        st.sidebar.header("Filters")
        timeframe = st.sidebar.selectbox(
            "Timeframe",
            ["1 Hour", "4 Hours", "24 Hours", "7 Days"]
        )
        
        # Main content
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_fear_greed_gauge()
            self.render_trending_tickers()
        
        with col2:
            self.render_unusual_activity()
            self.render_platform_breakdown()
        
        # Detailed ticker analysis
        st.header("Ticker Deep Dive")
        ticker = st.text_input("Enter ticker symbol", "AAPL")
        if ticker:
            self.render_ticker_analysis(ticker, timeframe)
    
    def render_fear_greed_gauge(self):
        """Render Fear & Greed Index gauge"""
        st.subheader("Market Sentiment Index")
        
        # Fetch current value
        current_value = self.fetch_fear_greed_index()
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Fear & Greed"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 20], 'color': "darkred"},
                    {'range': [20, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "gray"},
                    {'range': [60, 80], 'color': "lightgreen"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_trending_tickers(self):
        """Show most mentioned tickers"""
        st.subheader("Trending Tickers (24h)")
        
        trending = self.fetch_trending_tickers()
        
        df = pd.DataFrame(trending)
        df['sentiment_emoji'] = df['avg_sentiment'].apply(
            lambda x: '🟢' if x > 0.2 else '🔴' if x < -0.2 else '⚪'
        )
        
        st.dataframe(
            df[['sentiment_emoji', 'ticker', 'mentions', 'avg_sentiment']],
            use_container_width=True
        )
    
    def render_ticker_analysis(self, ticker: str, timeframe: str):
        """Detailed analysis for specific ticker"""
        data = self.fetch_ticker_data(ticker, timeframe)
        
        if data.empty:
            st.warning(f"No data available for {ticker}")
            return
        
        # Sentiment over time chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['sentiment_score'],
            mode='lines+markers',
            name='Sentiment',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title=f"{ticker} Sentiment Over Time",
            xaxis_title="Time",
            yaxis_title="Sentiment Score",
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=data['timestamp'],
            y=data['volume'],
            name='Mention Volume',
            marker_color='lightblue'
        ))
        fig2.update_layout(
            title=f"{ticker} Mention Volume",
            xaxis_title="Time",
            yaxis_title="Number of Mentions"
        )
        st.plotly_chart(fig2, use_container_width=True)
