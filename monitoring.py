#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText
from slack_sdk import WebClient

class AlertingSystem:
    """
    Alert traders/analysts to unusual market sentiment
    """
    def __init__(self):
        self.slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.email_config = {
            'server': os.getenv('SMTP_SERVER'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD')
        }
        
    async def check_and_alert(self):
        """Run periodic checks and send alerts"""
        # Check for unusual activity
        unusual_activity = await self.get_unusual_activity()
        
        for alert in unusual_activity:
            if alert['severity'] == 'high' and not alert['notified']:
                await self.send_alert(alert)
                await self.mark_as_notified(alert['id'])
    
    async def send_alert(self, alert: dict):
        """Send alert via Slack and Email"""
        message = self.format_alert_message(alert)
        
        # Slack
        await self.send_slack_alert(message, alert['severity'])
        
        # Email for high severity
        if alert['severity'] == 'high':
            await self.send_email_alert(message, alert)
    
    async def send_slack_alert(self, message: str, severity: str):
        """Post to Slack channel"""
        channel = '#sentiment-alerts'
        
        # Color code by severity
        colors = {'low': '#36a64f', 'medium': '#ff9800', 'high': '#f44336'}
        
        self.slack_client.chat_postMessage(
            channel=channel,
            text=message,
            attachments=[{
                'color': colors[severity],
                'text': message
            }]
        )
    
    async def send_email_alert(self, message: str, alert: dict):
        """Send email to portfolio managers"""
        recipients = ['pm@hedgefund.com', 'traders@hedgefund.com']
        
        msg = MIMEText(message)
        msg['Subject'] = f"[URGENT] Sentiment Alert: {alert['ticker']}"
        msg['From'] = self.email_config['username']
        msg['To'] = ', '.join(recipients)
        
        with smtplib.SMTP(self.email_config['server'], 
                         self.email_config['port']) as server:
            server.starttls()
            server.login(self.email_config['username'], 
                        self.email_config['password'])
            server.send_message(msg)
    
    def format_alert_message(self, alert: dict) -> str:
        """Format alert for readability"""
        return f"""
🚨 Unusual Activity Detected

Ticker: {alert['ticker']}
Alert Type: {alert['alert_type']}
Severity: {alert['severity'].upper()}
Time: {alert['timestamp']}

Details:
{json.dumps(alert['details'], indent=2)}

View Dashboard: https://sentiment.hedgefund.internal/ticker/{alert['ticker']}
        """
