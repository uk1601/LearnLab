from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import select, func, desc, and_, distinct, case
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from ...core.logger import setup_logger, log_error
from ...models.quiz import (
    Quiz, Question, QuestionConcept, QuizAttempt, 
    QuestionResponse, MultipleChoiceOption, SubjectiveAnswer
)
from ...models.file import File
from ...schemas.quiz import FileQuizStats, QuizAnalytics, QuizProgressStats

logger = setup_logger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = setup_logger(__name__)
    
    def execute_query(self, query, params=None):
        """Helper method for executing queries"""
        with self.db.begin():
            result = self.db.execute(query, params or {})
            return result.fetchall()
    
    def get_file_quiz_stats(self, file_id: UUID) -> FileQuizStats:
        """Get quiz statistics for a file"""
        logger.info(f"Generating quiz stats for file {file_id}")
        
        try:
            # Build query using SQLAlchemy ORM
            file_query = (
                select(
                    File.id.label('file_id'),
                    File.filename,
                    func.count(distinct(Quiz.id)).label('total_quizzes'),
                    func.count(distinct(Question.id)).label('total_questions'),
                    func.count(distinct(QuizAttempt.id)).label('total_attempts'),
                    func.avg(QuizAttempt.score).label('average_score'),
                    func.count(distinct(QuizAttempt.user_id)).label('unique_participants'),
                    func.sum(QuestionResponse.time_taken).label('total_time_spent'),
                    func.count(distinct(QuestionConcept.concept)).label('unique_concepts'),
                    func.sum(case((Question.question_type == 'multiple_choice', 1), else_=0)).label('mc_count'),
                    func.sum(case((Question.question_type == 'subjective', 1), else_=0)).label('subj_count'),
                    (func.avg(case((QuestionResponse.is_correct == True, 1), else_=0)) * 100).label('success_rate')
                )
                .select_from(File)
                .outerjoin(Quiz, Quiz.file_id == File.id)
                .outerjoin(Question, Question.quiz_id == Quiz.id)
                .outerjoin(QuestionConcept, QuestionConcept.question_id == Question.id)
                .outerjoin(QuizAttempt, QuizAttempt.quiz_id == Quiz.id)
                .outerjoin(QuestionResponse, QuestionResponse.question_id == Question.id)
                .where(and_(File.id == file_id, File.is_deleted == False))
                .group_by(File.id, File.filename)
            )

            result = self.db.execute(file_query)
            stats = result.fetchone()
            
            if not stats:
                logger.warning(f"No quiz stats found for file {file_id}")
                raise HTTPException(status_code=404, detail="File not found or has no quizzes")

            return FileQuizStats(
                file_id=file_id,
                filename=stats.filename,
                total_quizzes=stats.total_quizzes or 0,
                total_questions=stats.total_questions or 0,
                total_attempts=stats.total_attempts or 0,
                average_score=stats.average_score,
                unique_participants=stats.unique_participants or 0,
                total_time_spent=stats.total_time_spent or 0,
                unique_concepts=stats.unique_concepts or 0,
                multiple_choice_count=stats.mc_count or 0,
                subjective_count=stats.subj_count or 0,
                success_rate=stats.success_rate or 0.0
            )
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'file_id': str(file_id),
                'operation': 'get_file_quiz_stats'
            })
            raise HTTPException(status_code=500, detail="Failed to generate quiz statistics")

    def get_quiz_analytics(self, quiz_id: UUID) -> QuizAnalytics:
        """Get detailed analytics for a quiz"""
        logger.info(f"Generating detailed analytics for quiz {quiz_id}")
        
        try:
            # Get concept progress
            concepts_query = (
                select(
                    QuestionConcept.concept,
                    func.avg(case((QuestionResponse.is_correct == True, 1), else_=0)) * 100,
                    func.count(QuestionResponse.id),
                    func.max(QuestionResponse.created_at)
                )
                .join(Question, Question.id == QuestionConcept.question_id)
                .outerjoin(QuestionResponse, QuestionResponse.question_id == Question.id)
                .where(Question.quiz_id == quiz_id)
                .group_by(QuestionConcept.concept)
            )
            
            concept_results = self.db.execute(concepts_query)
            concept_progress = {
                concept: {
                    'success_rate': float(success_rate or 0),
                    'attempts': attempts,
                    'last_attempt': last_attempt
                }
                for concept, success_rate, attempts, last_attempt in concept_results
            }

            # Get question analytics
            questions_query = (
                select(
                    Question.id,
                    Question.content,
                    func.avg(QuestionResponse.time_taken),
                    func.count(QuestionResponse.id),
                    func.avg(case((QuestionResponse.is_correct == True, 1), else_=0)) * 100,
                    func.avg(QuestionResponse.confidence_score)
                )
                .outerjoin(QuestionResponse, QuestionResponse.question_id == Question.id)
                .where(and_(Question.quiz_id == quiz_id, Question.is_active == True))
                .group_by(Question.id, Question.content)
            )
            
            question_results = self.db.execute(questions_query)
            question_analytics = [
                {
                    'id': q_id,
                    'content': content,
                    'average_time': float(avg_time or 0),
                    'total_attempts': attempts,
                    'success_rate': float(success_rate or 0),
                    'confidence_score': float(conf_score or 0)
                }
                for q_id, content, avg_time, attempts, success_rate, conf_score in question_results
            ]

            # Get overall stats
            # Get total unique users first
            total_users_query = (
                select(func.count(distinct(QuizAttempt.user_id)))
                .select_from(QuizAttempt)
                .where(QuizAttempt.status == 'completed')
            )
            total_users = self.db.execute(total_users_query).scalar() or 1  # Avoid division by zero

            # Then use it in the main stats query
            stats_query = (
                select(
                    func.count(distinct(QuizAttempt.id)),
                    func.avg(QuizAttempt.score),
                    (func.count(distinct(QuizAttempt.user_id)) * 100.0 / total_users),
                    func.avg(QuestionResponse.time_taken)
                )
                .select_from(QuizAttempt)
                .outerjoin(QuestionResponse, QuestionResponse.attempt_id == QuizAttempt.id)
                .where(and_(
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.status == 'completed'
                ))
            )            
            
            stats_result = self.db.execute(stats_query)
            total_attempts, avg_score, completion_rate, avg_time = stats_result.fetchone()

            return QuizAnalytics(
                total_attempts=total_attempts or 0,
                average_score=float(avg_score or 0),
                completion_rate=float(completion_rate or 0),
                average_time_per_question=int(avg_time or 0),
                concept_progress=concept_progress,
                question_analytics=question_analytics
            )
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'operation': 'get_quiz_analytics'
            })
            raise HTTPException(status_code=500, detail="Failed to generate quiz analytics")

    def get_quiz_progress_stats(
        self,
        quiz_id: UUID,
        user_id: Optional[UUID] = None
    ) -> QuizProgressStats:
        """Get quiz progress statistics over time"""
        logger.info(f"Generating progress stats for quiz {quiz_id}")
        
        try:
            # Base conditions
            conditions = [QuizAttempt.quiz_id == quiz_id]
            if user_id:
                conditions.append(QuizAttempt.user_id == user_id)
                
            # Get attempts over time
            attempts_query = (
                select(
                    func.date_trunc('day', QuizAttempt.created_at),
                    func.count(QuizAttempt.id)
                )
                .where(and_(*conditions))
                .group_by(func.date_trunc('day', QuizAttempt.created_at))
            )
            
            attempt_results = self.db.execute(attempts_query)
            attempts_over_time = {
                str(date): count
                for date, count in attempt_results
            }

            # Get score progression
            scores_query = (
                select(
                    func.date_trunc('day', QuizAttempt.created_at),
                    func.avg(QuizAttempt.score)
                )
                .where(and_(*conditions))
                .group_by(func.date_trunc('day', QuizAttempt.created_at))
            )
            
            score_results = self.db.execute(scores_query)
            score_progression = {
                str(date): float(score or 0)
                for date, score in score_results
            }

            # Get concept mastery trend
            concept_query = (
                select(
                    func.date_trunc('day', QuestionResponse.created_at),
                    QuestionConcept.concept,
                    func.avg(case((QuestionResponse.is_correct == True, 1), else_=0)) * 100
                )
                .select_from(Question)
                .join(QuestionConcept)
                .join(QuestionResponse)
                .where(and_(
                    Question.quiz_id == quiz_id,
                    QuestionResponse.user_id == user_id if user_id else True
                ))
                .group_by(
                    func.date_trunc('day', QuestionResponse.created_at),
                    QuestionConcept.concept
                )
            )
            
            concept_results = self.db.execute(concept_query)
            concept_mastery = {}
            for date, concept, mastery in concept_results:
                date_str = str(date)
                if date_str not in concept_mastery:
                    concept_mastery[date_str] = {}
                concept_mastery[date_str][concept] = float(mastery or 0)

            # Get common mistakes
            mistakes_query = (
                select(
                    Question.content,
                    QuestionResponse.response,
                    func.count().label('frequency')
                )
                .join(QuestionResponse)
                .where(and_(
                    Question.quiz_id == quiz_id,
                    QuestionResponse.is_correct == False,
                    QuestionResponse.user_id == user_id if user_id else True
                ))
                .group_by(Question.content, QuestionResponse.response)
                .order_by(desc('frequency'))
                .limit(10)
            )
            
            mistakes_results = self.db.execute(mistakes_query)
            common_mistakes = [
                {'question': q, 'wrong_answer': a}
                for q, a, _ in mistakes_results
            ]

            return QuizProgressStats(
                attempts_over_time=attempts_over_time,
                score_progression=score_progression,
                concept_mastery_trend=concept_mastery,
                common_mistakes=common_mistakes
            )
            
        except SQLAlchemyError as e:
            log_error(logger, e, {
                'quiz_id': str(quiz_id),
                'user_id': str(user_id) if user_id else None,
                'operation': 'get_quiz_progress_stats'
            })
            raise HTTPException(status_code=500, detail="Failed to generate progress statistics")