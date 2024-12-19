# app/api/v1/social.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ...schemas.social_schema import MarkdownContent, TwitterResponse, BloggerResponse, BlogContent
from ...services.social_service import SocialMediaService
from ...core.deps import get_current_user
from pydantic import BaseModel
from agents.utils.blog_agent import BlogAgent
from agents.utils.tweet_agent import TweetAgent
from agents.podcast_agent.learn_lab_assistant_agent import PodcastGenerator
import traceback
import os
from ...core.deps import get_db
from ...models.file import File as FileModel
from ...models.user import User
from uuid import UUID

router = APIRouter()
generator = PodcastGenerator()

class ContentRequest(BaseModel):
    query: str
    pdf_title: str

router = APIRouter()


@router.post("/twitter/thread", response_model=TwitterResponse)
async def post_twitter_thread(
    request: MarkdownContent,
    current_user = Depends(get_current_user)
):
    """
    Post a Twitter thread from markdown content
    """
    result = await SocialMediaService.post_twitter_thread(
        content=request.content,
        api_key=request.api_key,
        api_secret_key=request.api_secret_key,
        access_token=request.access_token,
        access_token_secret=request.access_token_secret
        )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
        
    return result

@router.post("/blogger/post", response_model=BloggerResponse)
async def post_blog(
    request: BlogContent,
    current_user = Depends(get_current_user)
):
    """
    Create a blog post from markdown content
    """
    result = await SocialMediaService.post_blog(request)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
        
    return result



@router.post("/generate/blog")
async def generate_blog(
    content_request: ContentRequest, 
    current_user: User= Depends(get_current_user),
    db : Session = Depends(get_db)):
    try:
        print(f"----------------------------\n")
        print(f"Generating blog for query: {content_request.query}")
        print(f"PDF Title: {content_request.pdf_title}")
        
        file = db.query(FileModel).filter(
            FileModel.id == content_request.pdf_title,
            FileModel.user_id == current_user.id,
            FileModel.is_deleted == False
        ).first()
        pdf_title = file.filename.rsplit('.', 1)[0]
        print(f"DEBUG File:{pdf_title}")
        print(f"DEBUG File:{file.id}")

        result = generator.generate_content(
            question=content_request.query,
            pdf_title=pdf_title,
            output_type="blog"
        )
        
        print(f"Blog Generation Completed....................\n")

        return result
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        print(f"ERROR Details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate/tweet")
async def generate_tweet(
    content_request: ContentRequest, 
    current_user: User= Depends(get_current_user),
    db : Session = Depends(get_db)):
    try:
        print(f"----------------------------\n")
        print(f"Generating tweet for query: {content_request.query}")
        print(f"PDF Title: {content_request.pdf_title}")
        
        file = db.query(FileModel).filter(
            FileModel.id == content_request.pdf_title,
            FileModel.user_id == current_user.id,
            FileModel.is_deleted == False
        ).first()
        pdf_title = file.filename.rsplit('.', 1)[0]
        print(f"DEBUG File:{pdf_title}")
        print(f"DEBUG File:{file.id}")
        result = generator.generate_content(
            question=content_request.query,
            pdf_title=pdf_title,
            output_type="tweet"
        )
        
        print(f"Tweet Generation Completed....................\n")
        
        return {
            "tweet": result.get('tweet_content', 'No tweet generated')
        }
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        print(f"ERROR Details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))






# @router.post("/generate/blog", response_model=BlogResponse)
# async def generate_blog(request: GenerationRequest, current_user = Depends(get_current_user)):
#     """
#     Generate blog content based on a given query.
#     """
#     try:
#         blog_agent = BlogAgent()
#         blog_content = blog_agent.generate_blog(request.query)
#         return {
#             "title": blog_content.title,
#             "body": blog_content.body
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

# @router.post("/generate/tweet", response_model=TweetResponse)
# async def generate_tweet(request: GenerationRequest, current_user = Depends(get_current_user)):
#     """
#     Generate a tweet based on a given query.
#     """
#     try:
#         tweet_agent = TweetAgent()
#         tweet_content = tweet_agent.generate_tweet(request.query)
#         return {
#             "tweet": tweet_content.tweet
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating tweet: {str(e)}")
