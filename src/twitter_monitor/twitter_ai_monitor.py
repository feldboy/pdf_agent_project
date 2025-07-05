"""
AI Twitter Monitoring Agent

This agent monitors Twitter for AI-related news and methodologies,
generates summaries, and delivers them via Telegram bot.

Features:
- Twitter timeline monitoring
- AI news identification and filtering
- Content summarization using LLM
- Telegram bot integration
- De-duplication and scheduling
"""

import tweepy
import asyncio
import logging
import sqlite3
import hashlib
import schedule
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from telegram import Bot
from telegram.error import TelegramError
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import requests
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_ai_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AINewsItem:
    """Data class for AI news items"""
    tweet_id: str
    author: str
    content: str
    url: str
    timestamp: datetime
    summary: str
    relevance_score: float
    hashtags: List[str]
    processed_at: datetime

@dataclass
class TwitterConfig:
    """Twitter API configuration"""
    bearer_token: str
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str

@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str
    chat_id: str

class TwitterAIMonitor:
    """Main AI Twitter monitoring agent"""
    
    def __init__(self, config_file: str = "twitter_monitor_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.db_path = "twitter_ai_monitor.db"
        self.processed_tweets: Set[str] = set()
        
        # AI keywords for filtering
        self.ai_keywords = {
            'primary': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'transformer', 'GPT', 'LLM', 'large language model',
                'ChatGPT', 'OpenAI', 'Anthropic', 'Claude', 'Gemini', 'LaMDA',
                'computer vision', 'natural language processing', 'NLP',
                'reinforcement learning', 'generative AI', 'AI breakthrough',
                'new AI model', 'AI research', 'paper release', 'arxiv',
                'AI methodology', 'AI technique', 'foundation model'
            ],
            'secondary': [
                'diffusion model', 'stable diffusion', 'DALL-E', 'midjourney',
                'AI agent', 'autonomous agent', 'multimodal', 'AGI',
                'AI safety', 'alignment', 'RLHF', 'fine-tuning',
                'prompt engineering', 'RAG', 'retrieval augmented',
                'vector database', 'embedding', 'attention mechanism',
                'self-supervised', 'few-shot', 'zero-shot', 'in-context learning'
            ]
        }
        
        # Trusted AI news sources (Twitter handles)
        self.trusted_sources = [
            'OpenAI', 'AnthropicAI', 'DeepMind', 'GoogleAI', 'MetaAI',
            'StabilityAI', 'HuggingFace', 'OpenResearch', 'paperswithcode',
            'AIatMeta', 'GoogleDeepMind', 'MSFTResearch', 'NVIDIAAIDev',
            'ylecun', 'karpathy', 'sama', 'demishassabis', 'jeffdean',
            'hardmaru', 'fchollet', 'tegmark', 'elonmusk', 'sundarpichai'
        ]
        
        self._init_database()
        self._init_apis()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "twitter": {
                "bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
                "consumer_key": os.getenv("TWITTER_CONSUMER_KEY", ""),
                "consumer_secret": os.getenv("TWITTER_CONSUMER_SECRET", ""),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
            },
            "telegram": {
                "bot_token": "7576198731:AAGIFMqo3JjLXXuEDs-603GMbT237EaK-CA",
                "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", "")
            },
            "monitoring": {
                "check_interval_minutes": 30,
                "summary_frequency": "daily",  # daily, twice_daily, immediate
                "max_tweets_per_check": 100,
                "relevance_threshold": 0.6
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in file_config:
                            default_config[key].update(file_config[key])
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        return default_config
    
    def _init_database(self):
        """Initialize SQLite database for storing processed tweets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_tweets (
                tweet_id TEXT PRIMARY KEY,
                author TEXT,
                content TEXT,
                url TEXT,
                timestamp TEXT,
                summary TEXT,
                relevance_score REAL,
                hashtags TEXT,
                processed_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                date TEXT PRIMARY KEY,
                summary TEXT,
                tweet_count INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Load processed tweet IDs
        self._load_processed_tweets()
    
    def _load_processed_tweets(self):
        """Load processed tweet IDs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT tweet_id FROM processed_tweets")
        self.processed_tweets = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        logger.info(f"Loaded {len(self.processed_tweets)} processed tweets")
    
    def _init_apis(self):
        """Initialize Twitter and Telegram APIs"""
        try:
            # Twitter API v2
            self.twitter_client = tweepy.Client(
                bearer_token=self.config["twitter"]["bearer_token"],
                consumer_key=self.config["twitter"]["consumer_key"],
                consumer_secret=self.config["twitter"]["consumer_secret"],
                access_token=self.config["twitter"]["access_token"],
                access_token_secret=self.config["twitter"]["access_token_secret"],
                wait_on_rate_limit=True
            )
            
            # Telegram Bot
            self.telegram_bot = Bot(token=self.config["telegram"]["bot_token"])
            
            # OpenAI Client
            self.openai_client = OpenAI(api_key=self.config["openai"]["api_key"])
            
            logger.info("APIs initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing APIs: {e}")
            raise
    
    def _calculate_relevance_score(self, tweet_text: str, author: str) -> float:
        """Calculate relevance score for a tweet"""
        score = 0.0
        text_lower = tweet_text.lower()
        
        # Check for primary keywords (higher weight)
        primary_matches = sum(1 for keyword in self.ai_keywords['primary'] 
                            if keyword.lower() in text_lower)
        score += primary_matches * 0.3
        
        # Check for secondary keywords (lower weight)
        secondary_matches = sum(1 for keyword in self.ai_keywords['secondary'] 
                              if keyword.lower() in text_lower)
        score += secondary_matches * 0.2
        
        # Bonus for trusted sources
        if author.lower() in [source.lower() for source in self.trusted_sources]:
            score += 0.4
        
        # Bonus for research paper mentions
        if any(term in text_lower for term in ['arxiv', 'paper', 'research', 'study']):
            score += 0.2
        
        # Bonus for breakthrough/new announcements
        if any(term in text_lower for term in ['breakthrough', 'new', 'announcing', 'release']):
            score += 0.2
        
        # Normalize score to 0-1 range
        return min(score, 1.0)
    
    def _is_ai_related(self, tweet_text: str, author: str) -> bool:
        """Determine if a tweet is AI-related"""
        relevance_score = self._calculate_relevance_score(tweet_text, author)
        threshold = self.config["monitoring"]["relevance_threshold"]
        return relevance_score >= threshold
    
    def _generate_summary(self, tweet_text: str, author: str) -> str:
        """Generate AI-powered summary of tweet content"""
        try:
            prompt = f"""
            Analyze this AI-related tweet and provide a concise summary focusing on:
            1. What's new or noteworthy
            2. The key AI concept, method, or news
            3. Why it matters in the AI field
            
            Tweet by @{author}:
            {tweet_text}
            
            Provide a 2-3 sentence summary that captures the essence and significance:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI expert who specializes in summarizing AI news and research developments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"AI-related content from @{author}: {tweet_text[:200]}..."
    
    def _extract_hashtags(self, tweet_text: str) -> List[str]:
        """Extract hashtags from tweet text"""
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, tweet_text)
    
    def fetch_recent_tweets(self) -> List[Dict]:
        """Fetch recent tweets from timeline and trusted sources"""
        tweets = []
        max_tweets = self.config["monitoring"]["max_tweets_per_check"]
        
        try:
            # Get tweets from home timeline
            timeline_tweets = self.twitter_client.get_home_timeline(
                max_results=min(max_tweets // 2, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities'],
                user_fields=['username', 'name']
            )
            
            if timeline_tweets.data:
                for tweet in timeline_tweets.data:
                    tweets.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'author': tweet.author_id,
                        'created_at': tweet.created_at,
                        'url': f"https://twitter.com/i/status/{tweet.id}"
                    })
            
            # Get tweets from specific AI-focused searches
            search_queries = [
                "artificial intelligence -is:retweet lang:en",
                "machine learning breakthrough -is:retweet lang:en",
                "new AI model -is:retweet lang:en",
                "OpenAI OR Anthropic OR DeepMind -is:retweet lang:en"
            ]
            
            for query in search_queries:
                search_tweets = self.twitter_client.search_recent_tweets(
                    query=query,
                    max_results=min(25, max_tweets // len(search_queries)),
                    tweet_fields=['created_at', 'author_id', 'public_metrics']
                )
                
                if search_tweets.data:
                    for tweet in search_tweets.data:
                        tweets.append({
                            'id': tweet.id,
                            'text': tweet.text,
                            'author': tweet.author_id,
                            'created_at': tweet.created_at,
                            'url': f"https://twitter.com/i/status/{tweet.id}"
                        })
            
            logger.info(f"Fetched {len(tweets)} tweets")
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    def process_tweets(self, tweets: List[Dict]) -> List[AINewsItem]:
        """Process tweets and identify AI-related content"""
        ai_news_items = []
        
        for tweet in tweets:
            tweet_id = str(tweet['id'])
            
            # Skip if already processed
            if tweet_id in self.processed_tweets:
                continue
            
            author = str(tweet['author'])
            content = tweet['text']
            
            # Check if AI-related
            if self._is_ai_related(content, author):
                try:
                    # Generate summary
                    summary = self._generate_summary(content, author)
                    
                    # Calculate relevance score
                    relevance_score = self._calculate_relevance_score(content, author)
                    
                    # Extract hashtags
                    hashtags = self._extract_hashtags(content)
                    
                    # Create AI news item
                    news_item = AINewsItem(
                        tweet_id=tweet_id,
                        author=author,
                        content=content,
                        url=tweet['url'],
                        timestamp=tweet['created_at'],
                        summary=summary,
                        relevance_score=relevance_score,
                        hashtags=hashtags,
                        processed_at=datetime.now()
                    )
                    
                    ai_news_items.append(news_item)
                    self.processed_tweets.add(tweet_id)
                    
                    # Store in database
                    self._store_news_item(news_item)
                    
                except Exception as e:
                    logger.error(f"Error processing tweet {tweet_id}: {e}")
        
        logger.info(f"Processed {len(ai_news_items)} AI-related tweets")
        return ai_news_items
    
    def _store_news_item(self, item: AINewsItem):
        """Store AI news item in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO processed_tweets 
            (tweet_id, author, content, url, timestamp, summary, relevance_score, hashtags, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.tweet_id,
            item.author,
            item.content,
            item.url,
            item.timestamp.isoformat(),
            item.summary,
            item.relevance_score,
            json.dumps(item.hashtags),
            item.processed_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def generate_daily_summary(self, date: str = None) -> str:
        """Generate a consolidated daily summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tweets from the specified date
        cursor.execute('''
            SELECT * FROM processed_tweets 
            WHERE date(processed_at) = ? 
            ORDER BY relevance_score DESC
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"No AI news found for {date}"
        
        # Prepare content for summary generation
        news_items = []
        for row in rows:
            news_items.append({
                'author': row[1],
                'summary': row[5],
                'relevance_score': row[6],
                'url': row[3]
            })
        
        # Generate consolidated summary using LLM
        try:
            news_text = "\n\n".join([
                f"• {item['summary']} (Source: @{item['author']}, Score: {item['relevance_score']:.2f})"
                for item in news_items[:10]  # Top 10 items
            ])
            
            prompt = f"""
            Create a comprehensive daily summary of AI news and developments based on these items:
            
            {news_text}
            
            Provide:
            1. A brief overview of the day's key AI developments
            2. Highlight the most significant breakthroughs or announcements
            3. Categorize updates by theme (new models, research, tools, etc.)
            4. Keep it concise but informative (3-4 paragraphs max)
            
            Format for Telegram with proper markdown:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI news curator creating daily summaries for AI professionals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            daily_summary = response.choices[0].message.content.strip()
            
            # Store daily summary
            self._store_daily_summary(date, daily_summary, len(news_items))
            
            return daily_summary
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return f"Daily AI News Summary for {date}\n\nFound {len(news_items)} AI-related updates today."
    
    def _store_daily_summary(self, date: str, summary: str, tweet_count: int):
        """Store daily summary in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summaries 
            (date, summary, tweet_count, created_at)
            VALUES (?, ?, ?, ?)
        ''', (date, summary, tweet_count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    async def send_telegram_message(self, message: str):
        """Send message via Telegram bot"""
        try:
            chat_id = self.config["telegram"]["chat_id"]
            if not chat_id:
                logger.error("Telegram chat ID not configured")
                return
            
            # Split message if too long
            max_length = 4000
            if len(message) > max_length:
                chunks = [message[i:i+max_length] for i in range(0, len(message), max_length)]
                for chunk in chunks:
                    await self.telegram_bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
            else:
                await self.telegram_bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            
            logger.info("Message sent to Telegram successfully")
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("Starting monitoring cycle")
        
        try:
            # Fetch recent tweets
            tweets = self.fetch_recent_tweets()
            
            if not tweets:
                logger.info("No tweets fetched")
                return
            
            # Process tweets for AI content
            ai_news_items = self.process_tweets(tweets)
            
            if not ai_news_items:
                logger.info("No AI-related content found")
                return
            
            # Handle immediate notifications if configured
            frequency = self.config["monitoring"]["summary_frequency"]
            
            if frequency == "immediate":
                # Send individual summaries immediately
                for item in ai_news_items:
                    message = f"🤖 *AI News Alert*\n\n{item.summary}\n\n📊 Relevance: {item.relevance_score:.2f}\n🔗 [View Tweet]({item.url})"
                    asyncio.run(self.send_telegram_message(message))
            
            logger.info(f"Monitoring cycle completed. Found {len(ai_news_items)} AI news items")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def send_daily_summary(self):
        """Generate and send daily summary"""
        try:
            summary = self.generate_daily_summary()
            
            message = f"📰 *Daily AI News Summary*\n{datetime.now().strftime('%Y-%m-%d')}\n\n{summary}"
            
            asyncio.run(self.send_telegram_message(message))
            logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    def start_scheduled_monitoring(self):
        """Start scheduled monitoring based on configuration"""
        frequency = self.config["monitoring"]["summary_frequency"]
        check_interval = self.config["monitoring"]["check_interval_minutes"]
        
        # Schedule monitoring checks
        schedule.every(check_interval).minutes.do(self.run_monitoring_cycle)
        
        # Schedule summary delivery
        if frequency == "daily":
            schedule.every().day.at("18:00").do(self.send_daily_summary)
        elif frequency == "twice_daily":
            schedule.every().day.at("12:00").do(self.send_daily_summary)
            schedule.every().day.at("18:00").do(self.send_daily_summary)
        
        logger.info(f"Scheduled monitoring started with {frequency} summaries")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run the Twitter AI Monitor"""
    try:
        monitor = TwitterAIMonitor()
        
        # Test configuration
        if not monitor.config["telegram"]["chat_id"]:
            print("⚠️  Telegram Chat ID not configured!")
            print("Please send '/start' to your bot and check the logs for your Chat ID")
        
        if not monitor.config["twitter"]["bearer_token"]:
            print("⚠️  Twitter API credentials not configured!")
            print("Please set up your Twitter API credentials in the environment variables")
        
        # Run initial monitoring cycle
        print("🚀 Running initial monitoring cycle...")
        monitor.run_monitoring_cycle()
        
        # Start scheduled monitoring
        print("⏰ Starting scheduled monitoring...")
        monitor.start_scheduled_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
