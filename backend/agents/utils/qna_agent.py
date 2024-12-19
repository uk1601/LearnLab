from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of possible answers")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation of why this is the correct answer")
    difficulty: str = Field(description="Difficulty level: easy, medium, or hard")

class QuizSet(BaseModel):
    title: str = Field(description="Title of the quiz")
    description: str = Field(description="Brief description of what the quiz covers")
    questions: List[QuizQuestion] = Field(description="List of quiz questions")
    total_points: int = Field(description="Total possible points for the quiz")
    recommended_time: int = Field(description="Recommended time in minutes")

class QuizGenerator:
    def __init__(self, api_key: str, model: str = "learnlm-1.5-pro-experimental", base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"):
        self.llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            temperature=0.7,
            api_key=api_key
        )
        
        self.quiz_generation_prompt = """
        Create a quiz based on the following context and question. The quiz should test understanding
        of key concepts and their applications.

        Context from document:
        {context}

        User's Question:
        {question}

        Requirements:
        1. Generate {num_questions} questions of varying difficulty
        2. Each question should have 4 options
        3. Include clear explanations for correct answers
        4. Ensure questions test different aspects: recall, understanding, and application
        5. Make sure all questions and answers are factually accurate based on the provided context
        6. Include a mix of difficulty levels

        Format the response as a QuizSet with:
        - A clear title related to the topic
        - A brief description
        - Questions with:
          - Question text
          - 4 options
          - Correct answer
          - Detailed explanation
          - Difficulty level
        - Total points (each question worth equal points)
        - Recommended time (roughly 1-2 minutes per question)

        Response Format:
        {format_instructions}
        """

    def generate_quiz(
        self,
        context: str,
        question: str,
        num_questions: int = 5
    ) -> QuizSet:
        """
        Generate a quiz based on the provided context and question.
        
        Args:
            context (str): The RAG context to base the quiz on
            question (str): The user's original question
            num_questions (int): Number of questions to generate
            
        Returns:
            QuizSet: A structured quiz with questions, answers, and metadata
        """
        print(f"\nGenerating quiz with {num_questions} questions..............")
        try:
            # Setup the parser
            parser = PydanticOutputParser(pydantic_object=QuizSet)
            prompt = ChatPromptTemplate.from_template(self.quiz_generation_prompt)
            
            # Format the prompt
            formatted_prompt = prompt.format_messages(
                context=context,
                question=question,
                num_questions=num_questions,
                format_instructions=parser.get_format_instructions()
            )
            
            # Generate quiz content
            response = self.llm.invoke(formatted_prompt)
            
            # Parse into QuizSet
            quiz_set = parser.parse(response.content)
            
            # Validate question count
            if len(quiz_set.questions) != num_questions:
                print(f"Warning: Generated {len(quiz_set.questions)} questions instead of requested {num_questions}")
            
            return quiz_set
            
        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            raise

    def grade_quiz(self, quiz: Dict[str, Any], user_answers: List[str]) -> Dict[str, Any]:
        """
        Grade a completed quiz and provide feedback.
        
        Args:
            quiz (Dict[str, Any]): The quiz dictionary containing questions and answers
            user_answers (List[str]): List of user's answers
                
        Returns:
            Dict with score and feedback
        """
        print("\nGrading quiz..............")
        if len(user_answers) != len(quiz['questions']):
            raise ValueError("Number of answers doesn't match number of questions")
                
        correct_count = 0
        feedback = []
            
        for i, (question, user_answer) in enumerate(zip(quiz['questions'], user_answers)):
            # Store correct answer in the question during quiz generation
            is_correct = user_answer == question.get('answer', '')  # Changed from correct_answer to answer
            if is_correct:
                correct_count += 1
                    
            feedback.append({
                "question_num": i + 1,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": question.get('answer', ''),  # Changed from correct_answer to answer
                "explanation": question.get('explanation', '')
            })
                
        score_percentage = (correct_count / len(quiz['questions'])) * 100
            
        return {
            "score": score_percentage,
            "correct_count": correct_count,
            "total_questions": len(quiz['questions']),
            "feedback": feedback
        }

    def format_quiz_for_display(self, quiz: QuizSet) -> Dict[str, Any]:
        """
        Format the quiz for display or API response with consistent answer field naming.
        """
        return {
            "title": quiz.title,
            "description": quiz.description,
            "total_points": quiz.total_points,
            "recommended_time": quiz.recommended_time,
            "questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "answer": q.correct_answer,  # Store as 'answer' consistently
                    "explanation": q.explanation,
                    "difficulty": q.difficulty
                }
                for q in quiz.questions
            ]
        }