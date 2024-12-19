import { create } from 'zustand';

interface FileStats {
  podcastStats: {
    total: number;
    completed: number;
    inProgress: number;
  };
  quizStats: {
    total: number;
    attempted: number;
    averageScore: number;
  };
  flashcardStats: {
    totalDecks: number;
    totalCards: number;
    masteredCards: number;
  };
}

interface WorkspaceState {
  // Statistics
  stats: FileStats;
  isLoading: boolean;
  error: string | null;

  // Actions
  setStats: (stats: Partial<FileStats>) => void;
  fetchStats: (fileId: string) => Promise<void>;
  clearError: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  // Initial state
  stats: {
    podcastStats: {
      total: 0,
      completed: 0,
      inProgress: 0
    },
    quizStats: {
      total: 0,
      attempted: 0,
      averageScore: 0
    },
    flashcardStats: {
      totalDecks: 0,
      totalCards: 0,
      masteredCards: 0
    }
  },
  isLoading: false,
  error: null,

  // Actions
  setStats: (stats) => set((state) => ({
    stats: {
      ...state.stats,
      ...stats
    }
  })),

  fetchStats: async (fileId: string) => {
    set({ isLoading: true, error: null });

    try {
      // TODO: Implement actual API calls when backend endpoints are ready
      const [podcastResponse, quizResponse, flashcardResponse] = await Promise.all([
        fetch(`/api/podcasts/stats/${fileId}`),
        fetch(`/api/quiz/stats/${fileId}`),
        fetch(`/api/flashcards/stats/${fileId}`)
      ]);

      const [podcastStats, quizStats, flashcardStats] = await Promise.all([
        podcastResponse.json(),
        quizResponse.json(),
        flashcardResponse.json()
      ]);

      set({
        stats: {
          podcastStats,
          quizStats,
          flashcardStats
        },
        isLoading: false
      });
    } catch (error) {
      set({
        error: 'Failed to fetch workspace statistics',
        isLoading: false
      });
    }
  },

  clearError: () => set({ error: null })
}));