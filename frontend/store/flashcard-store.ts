import { create } from 'zustand';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';

export interface Deck {
  id: string;
  title: string;
  description?: string;
  file_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  file_name: string;
  file_type: string;
  file_url: string;
}

export interface Flashcard {
  id: string;
  deck_id: string;
  front_content: string;
  back_content: string;
  page_number?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReviewResponse {
  id: string;
  user_id: string;
  flashcard_id: string;
  ease_factor: number;
  interval: number;
  repetitions: number;
  last_reviewed: string;
  next_review: string;
}

export interface DeckProgress {
  total_cards: number;
  mastered_cards: number;
  learning_cards: number;
  mastery_percentage: number;
  pages_covered: number[];
}

interface FlashcardStore {
  // Current state
  currentDeck: Deck | null;
  decks: Deck[];
  currentCard: Flashcard | null;
  deckProgress: DeckProgress | null;
  currentCardIndex: number;
  cardsInDeck: Flashcard[];
  isLoading: boolean;
  error: string | null;
  studySessionComplete: boolean;

  // Actions
  setCurrentDeck: (deck: Deck | null) => void;
  setDecks: (decks: Deck[]) => void;
  setCurrentCard: (card: Flashcard | null) => void;
  setDeckProgress: (progress: DeckProgress | null) => void;
  nextCard: () => void;
  resetStudySession: () => void;

  // API interactions
  fetchDecks: (fileId: string) => Promise<void>;
  fetchDeckCards: (deckId: string) => Promise<void>;
  fetchDeckProgress: (deckId: string) => Promise<void>;
  submitCardReview: (cardId: string, quality: number) => Promise<void>;
  createDeck: (fileId: string, title: string, description?: string) => Promise<void>;
}

export const useFlashcardStore = create<FlashcardStore>((set, get) => ({
  // Initial state
  currentDeck: null,
  decks: [],
  currentCard: null,
  deckProgress: null,
  currentCardIndex: 0,
  cardsInDeck: [],
  isLoading: false,
  error: null,
  studySessionComplete: false,

  // Actions
  setCurrentDeck: (deck) => {
    console.log('Setting current deck:', deck);
    set({ currentDeck: deck });
  },
  
  setDecks: (decks) => {
    console.log('Setting decks:', decks);
    set({ decks });
  },
  
  setCurrentCard: (card) => {
    console.log('Setting current card:', card);
    set({ currentCard: card });
  },
  
  setDeckProgress: (progress) => {
    console.log('Setting deck progress:', progress);
    set({ deckProgress: progress });
  },
  
  nextCard: () => {
    const { currentCardIndex, cardsInDeck } = get();
    console.log('Moving to next card:', { currentCardIndex, totalCards: cardsInDeck.length });
    
    const nextIndex = currentCardIndex + 1;
    if (nextIndex >= cardsInDeck.length) {
      console.log('Study session complete');
      set({ 
        studySessionComplete: true,
        currentCard: null 
      });
    } else {
      console.log('Setting next card:', cardsInDeck[nextIndex]);
      set({
        currentCardIndex: nextIndex,
        currentCard: cardsInDeck[nextIndex]
      });
    }
  },

  resetStudySession: () => {
    console.log('Resetting study session');
    set({
      currentCardIndex: 0,
      currentCard: null,
      studySessionComplete: false,
      cardsInDeck: []
    });
  },

  // API interactions
  fetchDecks: async (fileId: string) => {
    console.log('Fetching decks for file:', fileId);
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.flashcards.decks.list(fileId));
      if (!response.ok) throw new Error('Failed to fetch decks');
      const data = await response.json();
      console.log('Fetched decks:', data);
      set({ decks: data, isLoading: false });
    } catch (error) {
      console.error('Error fetching decks:', error);
      set({ error: 'Failed to fetch decks', isLoading: false });
      throw error;
    }
  },

  fetchDeckCards: async (deckId: string) => {
    console.log('Fetching cards for deck:', deckId);
    set({ isLoading: true, error: null });
    try {
      const deck = get().decks.find(d => d.id === deckId);
      if (deck) {
        set({ currentDeck: deck });
      }

      const response = await fetchClient(API_ROUTES.flashcards.decks.cards(deckId));
      if (!response.ok) throw new Error('Failed to fetch cards');
      const cards = await response.json();
      console.log('Fetched cards:', cards);
      
      set({ 
        cardsInDeck: cards,
        currentCardIndex: 0,
        currentCard: cards.length > 0 ? cards[0] : null,
        studySessionComplete: false,
        isLoading: false 
      });
    } catch (error) {
      console.error('Error fetching cards:', error);
      set({ error: 'Failed to fetch cards', isLoading: false });
      throw error;
    }
  },

  fetchDeckProgress: async (deckId: string) => {
    console.log('Fetching progress for deck:', deckId);
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.flashcards.decks.progress(deckId));
      if (!response.ok) throw new Error('Failed to fetch deck progress');
      const progress = await response.json();
      console.log('Fetched progress:', progress);
      set({ deckProgress: progress, isLoading: false });
    } catch (error) {
      console.error('Error fetching progress:', error);
      set({ error: 'Failed to fetch deck progress', isLoading: false });
      throw error;
    }
  },

  submitCardReview: async (cardId: string, quality: number) => {
    console.log('Submitting review:', { cardId, quality });
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.flashcards.cards.review(cardId), {
        method: 'POST',
        body: JSON.stringify({ quality })
      });
      if (!response.ok) throw new Error('Failed to submit review');
      console.log('Review submitted successfully');
      
      // Move to next card after successful review
      get().nextCard();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error submitting review:', error);
      set({ error: 'Failed to submit review', isLoading: false });
      throw error;
    }
  },

  createDeck: async (fileId: string, title: string, description?: string) => {
    console.log('Creating deck:', { fileId, title, description });
    set({ isLoading: true, error: null });
    try {
      const response = await fetchClient(API_ROUTES.flashcards.decks.list(fileId), {
        method: 'POST',
        body: JSON.stringify({ title, description, file_id: fileId })
      });
      if (!response.ok) throw new Error('Failed to create deck');
      const newDeck = await response.json();
      console.log('Created deck:', newDeck);
      set((state) => ({ 
        decks: [...state.decks, newDeck],
        isLoading: false 
      }));
    } catch (error) {
      console.error('Error creating deck:', error);
      set({ error: 'Failed to create deck', isLoading: false });
      throw error;
    }
  }
}));