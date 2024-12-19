# app/services/social_service.py

import os
import json
from typing import Dict
from ..utils.X import XPlatformClient
from ..utils.blogger import authenticate_blogger_api, get_blog_id, create_blog_post, read_markdown_file
from ..core.logger import setup_logger
from dotenv import load_dotenv
from ..utils.blogger import parse_markdown_content, convert_markdown_to_html
from ..schemas.social_schema import BlogContent, BloggerResponse, MarkdownContent, TwitterResponse
load_dotenv()


logger = setup_logger(__name__)
class SocialMediaService:
    @staticmethod
    async def post_twitter_thread(content: str, api_key: str, api_secret_key: str, access_token: str, access_token_secret: str) -> Dict:
        try:
            client = XPlatformClient(
                api_key=api_key,
                api_secret_key=api_secret_key,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Convert markdown to plain text
            plain_text = client.parse_markdown(content)
            tweet_ids = client.post_tweet_thread(plain_text)

            if not tweet_ids:
                return {
                    "success": False,
                    "message": "Failed to post thread",
                    "tweet_ids": None
                }

            return {
                "success": True,
                "message": f"Thread posted successfully with {len(tweet_ids)} tweets",
                "tweet_ids": tweet_ids
            }

        except Exception as e:
            logger.error(f"Error posting Twitter thread: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "tweet_ids": None
            }

    @staticmethod
    async def post_blog(content: str) -> Dict:
        try:
            # Initialize Blogger service
            service = authenticate_blogger_api()
            blog_id = get_blog_id(service)

            if not blog_id:
                return {
                    "success": False,
                    "message": "Could not retrieve blog ID",
                    "url": None
                }

            # Use parse_markdown_content instead of read_markdown_file
            title=content.title
            html_content=convert_markdown_to_html(content.body)
            
            if not title or not html_content:
                return {
                    "success": False,
                    "message": "Could not parse markdown content",
                    "url": None
                }

            result = create_blog_post(service, blog_id, title, html_content)
            
            return {
                "success": True,
                "message": "Blog post created successfully",
                "url": result.get('url')
            }

        except Exception as e:
            logger.error(f"Error creating blog post: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "url": None
            }