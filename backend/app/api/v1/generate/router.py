import os
import tempfile
import asyncio

import aiofiles
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from urllib.parse import urlparse

from ....models import Podcast
from ....schemas.flashcard import DeckCreate, FlashcardCreate
from ....schemas.quiz import (
    QuizCreate, QuizUpdate, QuizInDB,
    QuizWithDetails, QuizList, QuestionCreate,
    QuestionUpdate, QuestionInDB, QuestionWithOptions, QuestionWithAnswer,
    MultipleChoiceOptionCreate
)
from ....schemas.file import File, FileCreate, FileResponse
from ....models.file import File as FileModel
from app.core.deps import (
    get_db,
    get_current_user,
    get_audio_service,
    get_transcript_service
)
from app.core.logger import setup_logger, log_error
from app.models.user import User
from app.schemas.generate.models import GenerateRequest, GenerateResponse
from app.services.podcast_service import AudioService, TranscriptService
from app.services.quiz_service import QuizService, QuestionService
from app.services.flashcard_service import FlashcardService, DeckService, CardService
from agents.podcast_agent.learn_lab_assistant_agent import PodcastGenerator
from app.services.notification_service import notification_manager

logger = setup_logger(__name__)
router = APIRouter()
podcast_generator = PodcastGenerator()


async def _async_generate_podcast(
    file_id: UUID,
    query: str,
    db: Session,
    user_id: UUID,
    audio_service: AudioService,
    transcript_service: TranscriptService
):
    """Create a podcast from generated content (async)"""
    temp_file_path = None

    try:
        logger.info(f"Starting podcast generation for file {file_id}, query: {query}")
        file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.user_id == user_id,
            FileModel.is_deleted == False
        ).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        pdf_title = file.filename.rsplit('.', 1)[0]
        logger.debug(f"DEBUG File:{pdf_title}")
        logger.debug(f"DEBUG File:{file.id}")

        result = podcast_generator.generate_content(
            question=query,
            pdf_title=pdf_title,
            output_type="podcast"
        )

        try:
            url_parts = urlparse(result["s3_url"])
            s3_audio_key = url_parts.path.lstrip('/')
            logger.info(f"Extracted S3 key: {s3_audio_key}")
        except (KeyError, AttributeError) as e:
            logger.error(f"Failed to extract S3 key: {str(e)}")
            logger.error(f"Generator result: {result}")
            raise ValueError("Invalid generator output format") from e

        # In the original code, transcript processing and audio duration fetching
        # are commented out or not essential, so we keep them commented.

        # Create podcast record
        try:
            podcast = Podcast(
                file_id=file_id,
                user_id=user_id,
                title=result["topic"],
                description="Generated podcast from document query",
                duration=5000,  # Original code used a static duration
                s3_audio_key=s3_audio_key,
                s3_transcript_txt_key=" ",
                s3_transcript_vtt_key=" ",
                transcript_status='txt_only'
            )

            db.add(podcast)
            db.commit()
            db.refresh(podcast)
            logger.info(f"Created podcast record with ID: {podcast.id}")
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating podcast: {str(e)}")
            db.rollback()
            raise RuntimeError("Failed to create podcast record") from e

        # Send success notification
        try:
            await notification_manager.send_notification(
                user_id,
                {
                    "type": "notification",
                    "title": "Podcast Generated",
                    "message": f"Your podcast '{result['topic']}' has been generated successfully",
                    "variant": "success",
                    "duration": 5000
                }
            )
        except Exception as e:
            logger.error(f"Failed to send success notification: {str(e)}")

        return podcast

    except Exception as e:
        logger.error(f"Critical error in generate_podcast: {str(e)}", exc_info=True)

        # Attempt to send error notification
        try:
            await notification_manager.send_notification(
                user_id,
                {
                    "type": "notification",
                    "title": "Podcast Generation Failed",
                    "message": "Failed to generate podcast. Please try again.",
                    "variant": "destructive",
                    "duration": 5000
                }
            )
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {str(notify_error)}")

        raise
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary file: {str(e)}")


async def _async_generate_quiz(file_id: UUID, query: str, db: Session, user_id: UUID):
    try:
        logger.info(f"Starting quiz generation for file {file_id}")
        quiz_service = QuizService(db)
        question_service = QuestionService(db)

        file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.user_id == user_id,
            FileModel.is_deleted == False
        ).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        pdf_title = file.filename.rsplit('.', 1)[0]
        logger.debug(f"DEBUG File:{pdf_title}")
        logger.debug(f"DEBUG File:{file.id}")

        result = podcast_generator.generate_content(
            question=query,
            pdf_title=pdf_title,
            output_type="quiz"
        )

        quiz_data = QuizCreate(
            title=result['quiz']['title'],
            description=result['quiz']['description'],
            file_id=file_id
        )
        quiz = quiz_service.create_quiz(user_id, quiz_data)

        for q in result['quiz']['questions']:
            question_data = QuestionCreate(
                question_type="multiple_choice",
                content=q['question'],
                explanation=q['explanation'],
                concepts=[q['difficulty']],
                options=[
                    MultipleChoiceOptionCreate(
                        content=opt,
                        is_correct=(opt == q['answer'])
                    )
                    for opt in q['options']
                ]
            )
            await question_service.create_question(quiz.id, question_data)

        logger.info(f"Completed quiz generation for file {file_id}")

        await notification_manager.send_notification(
            user_id,
            {
                "type": "notification",
                "title": "Quiz Generated",
                "message": f"Your Quiz '{result['quiz']['title']}' has been generated successfully",
                "variant": "success",
                "duration": 5000
            }
        )

    except Exception as e:
        log_error(logger, e, {
            'operation': 'quiz_generation',
            'file_id': str(file_id),
            'user_id': str(user_id)
        })
        raise


async def _async_generate_flashcards(
    file_id: UUID,
    query: str,
    db: Session,
    user_id: UUID
):
    """Background task for flashcard generation (async)"""
    try:
        logger.info(f"Starting flashcard generation for file {file_id}")
        deck_service = DeckService(db)
        card_service = CardService(db)
        file = db.query(FileModel).filter(
            FileModel.id == file_id,
            FileModel.user_id == user_id,
            FileModel.is_deleted == False
        ).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        pdf_title = file.filename.rsplit('.', 1)[0]
        logger.debug(f"DEBUG File:{pdf_title}")
        logger.debug(f"DEBUG File:{file.id}")

        try:
            result = podcast_generator.generate_content(
                question=query,
                pdf_title=pdf_title,
                output_type="flashcards"
            )

            if not result.get('flashcards'):
                raise HTTPException(
                    status_code=500,
                    detail="No flashcards were generated"
                )

            logger.debug(f"Generated flashcard content for file {file_id}")

        except Exception as e:
            logger.error(f"Failed to generate flashcard content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating flashcards: {str(e)}"
            )

        deck_data = DeckCreate(
            title=result['flashcards']['title'],
            description=query,
            file_id=file_id
        )
        deck = deck_service.create_deck(user_id, deck_data)
        logger.debug(f"Created flashcard deck {deck.id} for file {file_id}")

        created_cards = 0
        for card in result['flashcards']['flashcards']:
            try:
                card_data = FlashcardCreate(
                    front_content=card['front'],
                    back_content=card['back'],
                    page_number=card.get('page_number'),
                    concepts=card.get('concepts', [])
                )
                card_service.create_flashcard(deck.id, card_data)
                created_cards += 1

            except Exception as e:
                logger.error(f"Failed to create flashcard in deck {deck.id}: {str(e)}")
                continue

        if created_cards == 0:
            logger.error(f"No flashcards were created for deck {deck.id}")
            deck_service.delete_deck(deck.id)
            raise HTTPException(
                status_code=500,
                detail="Failed to create any flashcards"
            )

        logger.info(f"Successfully created {created_cards} flashcards in deck {deck.id}")

        try:
            notification_data = {
                "type": "notification",
                "title": "Flashcards Generated",
                "message": f"Created {created_cards} flashcards in deck '{deck_data.title}'",
                "variant": "success"
            }
            await notification_manager.send_notification(user_id, notification_data)

        except Exception as e:
            logger.error(f"Failed to send completion notification: {str(e)}")

        return deck

    except HTTPException as e:
        raise e
    except Exception as e:
        log_error(logger, e, {
            'operation': 'flashcard_generation',
            'file_id': str(file_id),
            'user_id': str(user_id)
        })
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during flashcard generation: {str(e)}"
        )


# Synchronous wrappers for background tasks
def generate_podcast(
    file_id: UUID,
    query: str,
    db: Session,
    user_id: UUID,
    audio_service: AudioService,
    transcript_service: TranscriptService
):
    asyncio.run(_async_generate_podcast(file_id, query, db, user_id, audio_service, transcript_service))


def generate_quiz(file_id: UUID, query: str, db: Session, user_id: UUID):
    asyncio.run(_async_generate_quiz(file_id, query, db, user_id))


def generate_flashcards(file_id: UUID, query: str, db: Session, user_id: UUID):
    asyncio.run(_async_generate_flashcards(file_id, query, db, user_id))


@router.post("", response_model=GenerateResponse)
async def generate_learning_materials(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audio_service: AudioService = Depends(get_audio_service),
    transcript_service: TranscriptService = Depends(get_transcript_service)
):
    """
    Generate learning materials based on request parameters.
    Starts background tasks for selected generation types.
    Returns immediately while tasks run in the background.
    """
    logger.info(f"Received generation request for file {request.file_id}")

    try:
        response = GenerateResponse()

        if request.podcast:
            background_tasks.add_task(
                generate_podcast,
                request.file_id,
                request.query,
                db,
                current_user.id,
                audio_service,
                transcript_service
            )
            response.is_podcast_generating = True
            logger.info(f"Added podcast generation task for file {request.file_id}")

        if request.quiz:
            background_tasks.add_task(
                generate_quiz,
                request.file_id,
                request.query,
                db,
                current_user.id
            )
            response.is_quiz_generating = True
            logger.info(f"Added quiz generation task for file {request.file_id}")

        if request.flashcards:
            background_tasks.add_task(
                generate_flashcards,
                request.file_id,
                request.query,
                db,
                current_user.id
            )
            response.is_flashcards_generating = True
            logger.info(f"Added flashcard generation task for file {request.file_id}")

        return response

    except Exception as e:
        log_error(logger, e, {
            'operation': 'generate_learning_materials',
            'file_id': str(request.file_id),
            'user_id': str(current_user.id),
            'request': request.dict()
        })
        raise HTTPException(status_code=500, detail="Failed to start generation tasks")