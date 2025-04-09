export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://backend:8000" || "http://localhost:8000" ;
console.log('-----------API_BASE_URL----------', API_BASE_URL);
export const API_ROUTES = {
  auth: {
    base: `${API_BASE_URL}/auth`,
    login: `${API_BASE_URL}/auth/login`,
    register: `${API_BASE_URL}/auth/register`,
    me: `${API_BASE_URL}/auth/me`,
    logout: `${API_BASE_URL}/auth/logout`
  },
  files: {
    base: `${API_BASE_URL}/api/files`,
    upload: `${API_BASE_URL}/api/files/upload`,
    list: `${API_BASE_URL}/api/files/files`,
    delete: (id: string) => `${API_BASE_URL}/api/files/files/${id}`,
    get: (id: string) => `${API_BASE_URL}/api/files/files/${id}`,
  },
  podcasts: {
    base: `${API_BASE_URL}/api/podcasts`,
    list: `${API_BASE_URL}/api/podcasts`,
    get: (id: string) => `${API_BASE_URL}/api/podcasts/${id}`,
  },
  quiz: {
    base: `${API_BASE_URL}/api/quiz`,
    list: (fileId?: string) => fileId 
      ? `${API_BASE_URL}/api/quiz?file_id=${fileId}` 
      : `${API_BASE_URL}/api/quiz`,
    questions: (quizId: string) => `${API_BASE_URL}/api/quiz/questions/${quizId}`,
    attempts: {
      create: `${API_BASE_URL}/api/quiz/attempts`,
      submitResponse: (attemptId: string) => `${API_BASE_URL}/api/quiz/attempts/${attemptId}/responses`,
      complete: (attemptId: string) => `${API_BASE_URL}/api/quiz/attempts/${attemptId}`,
    }
  },
  flashcards: {
    base: `${API_BASE_URL}/api/flashcards`,
    decks: {
      list: (fileId: string) => `${API_BASE_URL}/api/flashcards/decks/${fileId}`,
      get: (deckId: string) => `${API_BASE_URL}/api/flashcards/decks/${deckId}`,
      progress: (deckId: string) => `${API_BASE_URL}/api/flashcards/decks/${deckId}/progress`,
      cards: (deckId: string) => `${API_BASE_URL}/api/flashcards/decks/${deckId}/cards`,
    },
    cards: {
      update: (cardId: string) => `${API_BASE_URL}/api/flashcards/cards/${cardId}`,
      review: (cardId: string) => `${API_BASE_URL}/api/flashcards/cards/${cardId}/review`,
    },
    stats: `${API_BASE_URL}/api/flashcards/stats`,
    learningStatus: (fileId: string) => `${API_BASE_URL}/api/flashcards/files/${fileId}/learning-status`,
  }
};