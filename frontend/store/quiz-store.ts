import { create } from 'zustand';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';

export interface Quiz {
  id: string;
  title: string;
  description?: string;
  file_id: string;
  user_id: string;
  is_active: boolean;
  file_name: string;
  total_questions: number;
  total_attempts: number;
  average_score?: number;
  highest_score?: number;
  last_attempt?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionBase {
  id: string;
  quiz_id: string;
  question_type: 'multiple_choice' | 'subjective';
  content: string;
  explanation: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  concepts: QuestionConcept[];
}

export interface MultipleChoiceOption {
  id: string;
  question_id: string;
  content: string;
  is_correct: boolean;
  created_at: string;
}

export interface SubjectiveAnswer {
  id: string;
  question_id: string;
  answer: string;
  created_at: string;
}

export interface QuestionConcept {
  id: string;
  question_id: string;
  concept: string;
}

export interface QuestionWithOptions extends QuestionBase {
  question_type: 'multiple_choice';
  multiple_choice_options: MultipleChoiceOption[];
}

export interface QuestionWithAnswer extends QuestionBase {
  question_type: 'subjective';
  subjective_answer: SubjectiveAnswer;
}

export type Question = QuestionWithOptions | QuestionWithAnswer;

export interface QuestionResponse {
  id: string;
  attempt_id: string;
  question_id: string;
  response: string;
  is_correct: boolean;
  confidence_score?: number;
  time_taken: number;
  created_at: string;
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  score?: number;
  status: 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
}

interface QuizStore {
  // Quiz list management
  quizzes: Quiz[];
  currentQuiz: Quiz | null;
  
  // Attempt management
  currentAttempt: QuizAttempt | null;
  questions: Question[];
  currentQuestionIndex: number;
  responses: Record<string, QuestionResponse>;
  
  // Quiz flow state
  isLoading: boolean;
  error: string | null;
  submittingResponse: boolean;
  
  // Basic actions
  setCurrentQuiz: (quiz: Quiz | null) => void;
  setQuizzes: (quizzes: Quiz[]) => void;
  setCurrentAttempt: (attempt: QuizAttempt | null) => void;
  setQuestions: (questions: Question[]) => void;
  setCurrentQuestionIndex: (index: number) => void;
  addResponse: (response: QuestionResponse) => void;
  reset: () => void;
  
  // API actions
  fetchQuizzes: (fileId: string) => Promise<void>;
  startQuiz: (quizId: string) => Promise<void>;
  fetchQuestions: (quizId: string) => Promise<void>;
  submitResponse: (questionId: string, response: string, timeTaken: number) => Promise<QuestionResponse>;
  completeQuiz: () => Promise<QuizAttempt>;
}

const initialState = {
  quizzes: [],
  currentQuiz: null,
  currentAttempt: null,
  questions: [],
  currentQuestionIndex: 0,
  responses: {},
  isLoading: false,
  error: null,
  submittingResponse: false,
};

export const useQuizStore = create<QuizStore>((set, get) => ({
  ...initialState,

  // Basic actions
  setCurrentQuiz: (quiz) => set({ currentQuiz: quiz }),
  setQuizzes: (quizzes) => set({ quizzes }),
  setCurrentAttempt: (attempt) => set({ currentAttempt: attempt }),
  setQuestions: (questions) => set({ questions }),
  setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),
  addResponse: (response) => set((state) => ({
    responses: { ...state.responses, [response.question_id]: response }
  })),
  reset: () => set(initialState),

  // API actions
  fetchQuizzes: async (fileId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.quiz.list(fileId));
      if (!response.ok) throw new Error('Failed to fetch quizzes');
      const data = await response.json();
      set({ quizzes: data.quizzes, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch quizzes', isLoading: false });
      throw error;
    }
  },

  startQuiz: async (quizId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.quiz.attempts.create, {
        method: 'POST',
        body: JSON.stringify({ quiz_id: quizId })
      });
      
      if (!response.ok) throw new Error('Failed to start quiz');
      const attempt = await response.json();
      
      // Reset attempt state
      set({
        currentAttempt: attempt,
        currentQuestionIndex: 0,
        responses: {},
        isLoading: false
      });
      
      // Fetch questions
      await get().fetchQuestions(quizId);
    } catch (error) {
      set({ error: 'Failed to start quiz', isLoading: false });
      throw error;
    }
  },

  fetchQuestions: async (quizId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.quiz.questions(quizId));
      if (!response.ok) throw new Error('Failed to fetch questions');
      const questions = await response.json();
      set({ questions, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch questions', isLoading: false });
      throw error;
    }
  },

  submitResponse: async (questionId: string, response: string, timeTaken: number) => {
    const { currentAttempt } = get();
    if (!currentAttempt) throw new Error('No active attempt');

    set({ submittingResponse: true, error: null });
    try {
      const responseData = {
        question_id: questionId,
        response,
        time_taken: timeTaken
      };

      const apiResponse = await fetchClient(
        API_ROUTES.quiz.attempts.submitResponse(currentAttempt.id), 
        {
          method: 'POST',
          body: JSON.stringify(responseData)
        }
      );
      
      if (!apiResponse.ok) {
        if (apiResponse.status === 400) {
          // Question already answered, fetch the existing response
          const existingResponse = get().responses[questionId];
          if (existingResponse) {
            set({ submittingResponse: false });
            return existingResponse;
          }
        }
        throw new Error('Failed to submit response');
      }

      const submittedResponse = await apiResponse.json();
      
      // Save response but don't advance to next question yet
      set((state) => ({
        responses: { ...state.responses, [questionId]: submittedResponse },
        submittingResponse: false
      }));

      return submittedResponse;
    } catch (error) {
      set({ error: 'Failed to submit response', submittingResponse: false });
      throw error;
    }
  },

  completeQuiz: async () => {
    const { currentAttempt } = get();
    if (!currentAttempt) throw new Error('No active attempt');

    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(
        API_ROUTES.quiz.attempts.complete(currentAttempt.id),
        { method: 'PATCH' }
      );
      
      if (!response.ok) throw new Error('Failed to complete quiz');
      const completedAttempt = await response.json();
      set({ currentAttempt: completedAttempt, isLoading: false });
      return completedAttempt;
    } catch (error) {
      set({ error: 'Failed to complete quiz', isLoading: false });
      throw error;
    }
  }
}));