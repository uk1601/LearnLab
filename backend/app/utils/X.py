import requests
import markdown
from requests_oauthlib import OAuth1
from html.parser import HTMLParser
import os
from typing import List, Optional
from dotenv import load_dotenv
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTMLStripper(HTMLParser):
    """A utility class to strip HTML tags from content."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

class XPlatformClient:
    """
    A client to interact with the X (formerly Twitter) platform.
    Supports posting and deleting tweets with rate limiting and retries.
    """
    # Rate limits: 50 requests per 15-minute window
    FIFTEEN_MINUTES = 900
    MAX_REQUESTS = 50

    def __init__(self, api_key: str, api_secret_key: str, access_token: str, access_token_secret: str):
        """Initialize the X Platform client with API credentials."""
        if not all([api_key, api_secret_key, access_token, access_token_secret]):
            raise ValueError("All API credentials must be provided")

        self.auth = OAuth1(api_key, api_secret_key, access_token, access_token_secret)
        self.post_url = "https://api.x.com/2/tweets"

    @staticmethod
    def strip_html_tags(html_content: str) -> str:
        """Strip HTML tags from the given content and return plain text."""
        if not html_content:
            return ""
        stripper = HTMLStripper()
        stripper.feed(html_content)
        return stripper.get_data()

    def parse_markdown(self, markdown_content: str) -> str:
        """Convert Markdown content to plain text by stripping HTML tags."""
        if not markdown_content:
            return ""
        try:
            html_content = markdown.markdown(markdown_content)
            return self.strip_html_tags(html_content)
        except Exception as e:
            logger.error(f"Error parsing markdown: {e}")
            raise

    def split_text_into_chunks(self, content: str, max_length: int = 280) -> List[str]:
        """
        Split the content into logical chunks without cutting off sentences.
        
        Args:
            content: Text to split
            max_length: Maximum length of each chunk (default: 280)
            
        Returns:
            List of text chunks
        """
        if not content:
            return []
            
        if max_length < 10:
            raise ValueError("max_length must be at least 10 characters")

        chunks = []
        while len(content) > max_length:
            # Try to split at last sentence
            last_period = content[:max_length].rfind('. ')
            last_space = content[:max_length].rfind(' ')
            
            # Prefer sentence splits over word splits
            split_index = last_period + 1 if last_period != -1 else last_space
            
            # If no good split found, force split at max_length
            if split_index == -1:
                split_index = max_length

            chunks.append(content[:split_index].strip())
            content = content[split_index:].strip()

        if content:
            chunks.append(content)

        return chunks

    @on_exception(expo, RateLimitException, max_tries=5)
    @limits(calls=MAX_REQUESTS, period=FIFTEEN_MINUTES)
    def post_tweet(self, text: str, in_reply_to_id: Optional[str] = None) -> Optional[str]:
        """
        Post a single tweet with rate limiting and retries.
        
        Args:
            text: Tweet content
            in_reply_to_id: Optional ID of tweet to reply to
            
        Returns:
            Tweet ID if successful, None otherwise
        """
        payload = {"text": text}
        if in_reply_to_id:
            payload["reply"] = {"in_reply_to_tweet_id": in_reply_to_id}

        try:
            response = requests.post(
                self.post_url,
                auth=self.auth,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            tweet_id = response.json()["data"]["id"]
            logger.info(f"Tweet posted successfully: {tweet_id}")
            return tweet_id

        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting tweet: {e}")
            return None

    def post_tweet_thread(self, content: str) -> List[str]:
        """
        Post a thread of tweets.
        
        Args:
            content: Content to post as thread
            
        Returns:
            List of posted tweet IDs
        """
        chunks = self.split_text_into_chunks(content)
        if not chunks:
            logger.warning("No content to post")
            return []

        thread_ids = []
        in_reply_to_id = None

        for chunk in chunks:
            tweet_id = self.post_tweet(chunk, in_reply_to_id)
            if tweet_id:
                thread_ids.append(tweet_id)
                in_reply_to_id = tweet_id
            else:
                logger.error(f"Failed to post chunk. Thread incomplete after {len(thread_ids)} tweets")
                break

        return thread_ids

    @on_exception(expo, RateLimitException, max_tries=3)
    @limits(calls=MAX_REQUESTS, period=FIFTEEN_MINUTES)
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet by ID with rate limiting and retries.
        
        Args:
            tweet_id: ID of tweet to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delete_url = f"{self.post_url}/{tweet_id}"
            response = requests.delete(delete_url, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Tweet {tweet_id} deleted successfully")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting tweet {tweet_id}: {e}")
            return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # X API credentials
    API_KEY = os.getenv('X_API_KEY')
    API_SECRET_KEY = os.getenv('X_API_SECRET_KEY')
    ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

    try:
        # Instantiate the client
        client = XPlatformClient(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # Read and parse the markdown file
        with open("post.md", "r", encoding='utf-8') as md_file:
            md_content = md_file.read()

        # Convert Markdown to plain text and post thread
        plain_text = client.parse_markdown(md_content)
        tweet_ids = client.post_tweet_thread(plain_text)
        
        logger.info(f"Posted thread with {len(tweet_ids)} tweets")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")