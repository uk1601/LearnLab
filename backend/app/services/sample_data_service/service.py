from datetime import datetime
import json
import os
from typing import Dict, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from ...core.logger import setup_logger, log_error
from ...models.file import File
from ...models.flashcard import FlashcardDeck, Flashcard, LearningProgress
from ...models.quiz import Quiz, Question, QuestionConcept, QuizAttempt, QuestionResponse
from ...models.quiz.question import MultipleChoiceOption, SubjectiveAnswer
from ...models.podcast import Podcast, PodcastProgress, PodcastAnalytics
from ...services.s3 import S3Service
from ...models.file import File as FileModel

logger = setup_logger(__name__)

class SampleDataService:
    def __init__(self, db: Session, s3_service: S3Service):
        self.db = db
        self.s3_service = s3_service
        # Get base path for sample data
        self.base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
            'sample_data'
        )
        
    async def populate_user_data(self, user_id: UUID) -> Dict:
        """
        Populate sample data for a user
        Returns a summary of created data
        """
        logger.info(f"Starting sample data population for user {user_id}")
        
        try:
            # Create sample files
            files = self.db.query(FileModel).filter(
                FileModel.user_id == user_id,
                FileModel.is_deleted == False
            ).offset(0).limit(10).all()
            
            # Initialize summary
            summary = {
                "files_created": len(files),
                "flashcard_decks": 0,
                "total_cards": 0,
                "quizzes": 0,
                "total_questions": 0,
                "podcasts": 0
            }
            
            # Create learning content for each file
            for file in files:
                # Create flashcards
                decks, cards = await self._create_flashcard_content(user_id, file.id)
                summary["flashcard_decks"] += decks
                summary["total_cards"] += cards
                
                # # Create quizzes
                quizzes, questions = await self._create_quiz_content(user_id, file.id)
                summary["quizzes"] += quizzes
                summary["total_questions"] += questions
                
                # # Create podcasts
                # podcasts = await self._create_podcast_content(user_id, file.id)
                # summary["podcasts"] += podcasts
            
            return {
                "status": "success",
                "message": "Sample data populated successfully",
                "summary": summary
            }
            
        except Exception as e:
            log_error(logger, e, {
                'user_id': str(user_id),
                'operation': 'populate_user_data'
            })
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to populate sample data: {str(e)}"
            )

    # async def _create_sample_files(self, user_id: UUID) -> List[File]:
    #     """Create sample files for the user"""
    #     logger.info(f"Creating sample files for user {user_id}")
        
    #     files = []
    #     sample_files_dir = os.path.join(self.base_path, 'files')
        
    #     try:
    #         # For each PDF in the sample_files directory
    #         for filename in os.listdir(sample_files_dir):
    #             if filename.endswith('.pdf'):
    #                 file_path = os.path.join(sample_files_dir, filename)
    #                 file_response = UploadFile(
    #                     filename=filename,
    #                     file_size=os.path.getsize(file_path),
    #                     s3_key=None,
    #                     user_id=user_id
    #                 )
    #                 # Upload to S3
    #                 s3_key = await s3_service.upload_file(file, current_user.id)
                    
    #                 # Create file record
    #                 file = File(
    #                     user_id=user_id,
    #                     filename=filename,
    #                     s3_key=s3_key,
    #                     file_size=os.path.getsize(file_path),
    #                     mime_type="application/pdf"
    #                 )
    #                 self.db.add(file)
    #                 self.db.flush()
    #                 files.append(file)
            
    #         self.db.commit()
    #         return files
            
    #     except Exception as e:
    #         self.db.rollback()
    #         log_error(logger, e, {
    #             'user_id': str(user_id),
    #             'operation': 'create_sample_files'
    #         })
    #         raise

    async def _create_flashcard_content(self, user_id: UUID, file_id: UUID) -> Tuple[int, int]:
        """Create sample flashcard content"""
        logger.info(f"Creating flashcard content for file {file_id}")
        
        try:
            # Load flashcard data
            with open(os.path.join(self.base_path, 'flashcards.json'), 'r') as f:
                flashcard_data = json.load(f)
            
            total_decks = 0
            total_cards = 0
            
            for deck_id, deck_data in flashcard_data.items():
                # Create deck
                deck = FlashcardDeck(
                    user_id=user_id,
                    file_id=file_id,
                    title=deck_data['title'],
                    description=deck_data['description']
                )
                self.db.add(deck)
                self.db.flush()
                total_decks += 1
                
                # Create cards
                for card_data in deck_data['cards']:
                    card = Flashcard(
                        deck_id=deck.id,
                        front_content=card_data['front_content'],
                        back_content=card_data['back_content'],
                        page_number=card_data.get('page_number')
                    )
                    self.db.add(card)
                    total_cards += 1
                    
                    # Create initial learning progress
                    progress = LearningProgress(
                        user_id=user_id,
                        flashcard_id=card.id,
                        ease_factor=2.5,
                        interval=0,
                        repetitions=0,
                        next_review=datetime.utcnow()
                    )
                    self.db.add(progress)
            
            self.db.commit()
            return total_decks, total_cards
            
        except Exception as e:
            self.db.rollback()
            log_error(logger, e, {
                'file_id': str(file_id),
                'operation': 'create_flashcard_content'
            })
            raise

    async def _create_quiz_content(self, user_id: UUID, file_id: UUID) -> Tuple[int, int]:
        """Create sample quiz content"""
        logger.info(f"Creating quiz content for file {file_id}")
        
        try:
            # Load quiz data
            with open(os.path.join(self.base_path, 'quizzes.json'), 'r') as f:
                quiz_data = json.load(f)
            
            total_quizzes = 0
            total_questions = 0
            
            for quiz_id, quiz_info in quiz_data.items():
                # Create quiz
                quiz = Quiz(
                    user_id=user_id,
                    file_id=file_id,
                    title=quiz_info['title'],
                    description=quiz_info['description']
                )
                self.db.add(quiz)
                self.db.flush()
                total_quizzes += 1
                
                # Create questions
                for q_data in quiz_info['questions']:
                    question = Question(
                        quiz_id=quiz.id,
                        question_type=q_data['question_type'],
                        content=q_data['content'],
                        explanation=q_data['explanation']
                    )
                    self.db.add(question)
                    self.db.flush()
                    total_questions += 1
                    
                    # Add concepts
                    for concept in q_data['concepts']:
                        concept_obj = QuestionConcept(
                            question_id=question.id,
                            concept=concept
                        )
                        self.db.add(concept_obj)
                    
                    # Add options or answer based on question type
                    if q_data['question_type'] == 'multiple_choice':
                        for opt in q_data['options']:
                            option = MultipleChoiceOption(
                                question_id=question.id,
                                content=opt['content'],
                                is_correct=opt['is_correct']
                            )
                            self.db.add(option)
                    else:  # subjective
                        answer = SubjectiveAnswer(
                            question_id=question.id,
                            answer=q_data['answer']
                        )
                        self.db.add(answer)
                
                # Create a sample attempt
                attempt = QuizAttempt(
                    quiz_id=quiz.id,
                    user_id=user_id,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    score=85.0,
                    status='completed'
                )
                self.db.add(attempt)
            
            self.db.commit()
            return total_quizzes, total_questions
            
        except Exception as e:
            self.db.rollback()
            log_error(logger, e, {
                'file_id': str(file_id),
                'operation': 'create_quiz_content'
            })
            raise

    async def _create_podcast_content(self, user_id: UUID, file_id: UUID) -> int:
        """Create sample podcast content"""
        logger.info(f"Creating podcast content for file {file_id}")
        
        try:
            # Load podcast data
            with open(os.path.join(self.base_path, 'podcasts.json'), 'r') as f:
                podcast_data = json.load(f)
            
            total_podcasts = 0
            
            for podcast_id, podcast_info in podcast_data.items():
                # Upload audio file
                audio_filename = f"{podcast_id}.mp3"
                audio_path = os.path.join(self.base_path, 'audio', audio_filename)
                s3_audio_key = f"users/{user_id}/samples/audio/{audio_filename}"
                await self.s3_service.upload_file(audio_path, s3_audio_key)
                
                # Upload transcript files
                txt_filename = f"{podcast_id}.txt"
                vtt_filename = f"{podcast_id}.vtt"
                txt_path = os.path.join(self.base_path, 'transcripts', txt_filename)
                vtt_path = os.path.join(self.base_path, 'transcripts', vtt_filename)
                
                s3_txt_key = f"users/{user_id}/samples/transcripts/{txt_filename}"
                s3_vtt_key = f"users/{user_id}/samples/transcripts/{vtt_filename}"
                
                await self.s3_service.upload_file(txt_path, s3_txt_key)
                await self.s3_service.upload_file(vtt_path, s3_vtt_key)
                
                # Create podcast
                podcast = Podcast(
                    file_id=file_id,
                    user_id=user_id,
                    title=podcast_info['title'],
                    description=podcast_info['description'],
                    duration=podcast_info['duration'],
                    s3_audio_key=s3_audio_key,
                    s3_transcript_txt_key=s3_txt_key,
                    s3_transcript_vtt_key=s3_vtt_key,
                    transcript_status='vtt_ready'
                )
                self.db.add(podcast)
                self.db.flush()
                total_podcasts += 1
                
                # Create progress
                progress = PodcastProgress(
                    user_id=user_id,
                    podcast_id=podcast.id,
                    current_position=0,
                    playback_speed=1.0,
                    completed_segments=[],
                    completion_percentage=0.0
                )
                self.db.add(progress)
                
                # Create analytics
                analytics = PodcastAnalytics(
                    user_id=user_id,
                    podcast_id=podcast.id,
                    date=datetime.utcnow().date(),
                    total_time_listened=0,
                    average_speed=1.0,
                    number_of_sessions=0,
                    completion_rate=0.0
                )
                self.db.add(analytics)
            
            self.db.commit()
            return total_podcasts
            
        except Exception as e:
            self.db.rollback()
            log_error(logger, e, {
                'file_id': str(file_id),
                'operation': 'create_podcast_content'
            })
            raise