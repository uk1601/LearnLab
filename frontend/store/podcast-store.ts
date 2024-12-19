import { create } from 'zustand';
import { UUID } from 'crypto';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';

export interface PodcastProgress {
  id: UUID;
  user_id: UUID;
  podcast_id: UUID;
  current_position: number;
  playback_speed: number;
  completed_segments: number[];
  completion_percentage: number;
  last_played_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PodcastAnalytics {
  total_time_listened: number;
  average_speed: number;
  number_of_sessions: number;
  completion_rate: number;
  unique_listeners?: number;
  total_plays?: number;
  engagement_score?: number;
}

export interface Podcast {
  id: UUID;
  file_id: UUID;
  user_id: UUID;
  title: string;
  description?: string;
  duration: number;
  s3_audio_key: string;
  s3_transcript_txt_key: string;
  s3_transcript_vtt_key?: string;
  transcript_status: 'txt_only' | 'vtt_ready' | 'processing';
  total_plays: number;
  created_at: string;
  updated_at: string;
  // Extended properties from PodcastWithDetails
  audio_url?: string;
  transcript_txt_url?: string;
  transcript_vtt_url?: string;
  current_progress: number;
  current_speed: number;
}

interface PodcastStore {
  // Current playback state
  currentPodcast: Podcast | null;
  isPlaying: boolean;
  currentTime: number;
  volume: number;
  playbackRate: number;
  
  // Progress and analytics
  progress: PodcastProgress | null;
  analytics: PodcastAnalytics | null;
  
  // List management
  podcasts: Podcast[];
  
  // Actions
  setCurrentPodcast: (podcast: Podcast | null) => void;
  setIsPlaying: (isPlaying: boolean) => void;
  setCurrentTime: (time: number) => void;
  setVolume: (volume: number) => void;
  setPlaybackRate: (rate: number) => void;
  updateProgress: (progress: Partial<PodcastProgress>) => void;
  updateAnalytics: (analytics: Partial<PodcastAnalytics>) => void;
  setPodcasts: (podcasts: Podcast[]) => void;
  
  // API integration helpers
  fetchPodcasts: (file_id: string) => Promise<void>;
  updatePodcastProgress: (
    podcastId: UUID,
    position: number,
    speed: number
  ) => Promise<void>;
}

export const usePodcastStore = create<PodcastStore>((set, get) => ({
  // Initial states
  currentPodcast: null,
  isPlaying: false,
  currentTime: 0,
  volume: 1,
  playbackRate: 1,
  progress: null,
  analytics: null,
  podcasts: [],

  // Actions
  setCurrentPodcast: (podcast) => set({ currentPodcast: podcast }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setCurrentTime: (currentTime) => set({ currentTime }),
  setVolume: (volume) => set({ volume }),
  setPlaybackRate: (playbackRate) => set({ playbackRate }),
  
  updateProgress: (progressUpdate) => 
    set((state) => ({
      progress: state.progress 
        ? { ...state.progress, ...progressUpdate }
        : progressUpdate as PodcastProgress
    })),
    
  updateAnalytics: (analyticsUpdate) =>
    set((state) => ({
      analytics: state.analytics 
        ? { ...state.analytics, ...analyticsUpdate }
        : analyticsUpdate as PodcastAnalytics
    })),
    
  setPodcasts: (podcasts) => set({ podcasts }),

  // API integration
  fetchPodcasts: async (file_id) => {
    try {
      const response = await fetchClient(`${API_ROUTES.podcasts}`);
      if (!response.ok) throw new Error('Failed to fetch podcasts');
      const data = await response.json();
      set({ podcasts: data });
    } catch (error) {
      console.error('Error fetching podcasts:', error);
      // Could integrate with a toast notification system here
    }
  },

  updatePodcastProgress: async (podcastId, position, speed) => {
    
    try {
      const response = await fetchClient(`${API_ROUTES.podcasts.base}/${podcastId}/progress?position=${position}&speed=${speed}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) throw new Error('Failed to update progress');
      const progress = await response.json();
      set({ progress });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  }
}));