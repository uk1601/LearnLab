'use client';

import { useEffect, useRef } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { usePodcastStore } from '@/store/podcast-store';
import { useToast } from "@/hooks/use-toast";
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  Volume1, 
  VolumeX,
  Settings,
  RefreshCw
} from 'lucide-react';

const PLAYBACK_SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
const PROGRESS_UPDATE_INTERVAL = 15000; // 15 seconds
const SKIP_TIME = 10; // seconds

export function PodcastPlayer() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressInterval = useRef<NodeJS.Timeout>();
  const { toast } = useToast();

  const { 
    currentPodcast,
    isPlaying,
    currentTime,
    volume,
    playbackRate,
    setIsPlaying,
    setCurrentTime,
    setVolume,
    setPlaybackRate,
    updatePodcastProgress
  } = usePodcastStore();

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentPodcast) return;

    // Set initial values
    audio.volume = volume;
    audio.playbackRate = playbackRate;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleError = (e: ErrorEvent) => {
      console.error('Audio playback error:', e);
      toast({
        variant: "destructive",
        title: "Playback Error",
        description: "Failed to play audio. Please try again.",
      });
      setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    if (isPlaying) {
      audio.play().catch((error) => {
        console.error('Playback failed:', error);
        setIsPlaying(false);
        toast({
          variant: "destructive",
          title: "Playback Error",
          description: "Failed to start playback. Please try again.",
        });
      });
    } else {
      audio.pause();
    }

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [currentPodcast, isPlaying, volume, playbackRate, setCurrentTime, setIsPlaying, toast]);

  useEffect(() => {
    if (isPlaying && currentPodcast) {
      progressInterval.current = setInterval(async () => {
        const audio = audioRef.current;
        if (!audio) return;

        try {
          await updatePodcastProgress(
            currentPodcast.id,
            Math.floor(audio.currentTime),
            audio.playbackRate
          );
        } catch (error) {
          console.error('Failed to update progress:', error);
        }
      }, PROGRESS_UPDATE_INTERVAL);
    }

    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, [isPlaying, currentPodcast, updatePodcastProgress]);

  const handleSeekChange = (value: number[]) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = (value[0] / 100) * audio.duration;
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0] / 100;
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const skip = (seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = Math.max(0, Math.min(audio.currentTime + seconds, audio.duration));
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return h > 0
      ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
      : `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!currentPodcast) {
    return null;
  }

  return (
    <Card>
      <CardContent className="p-6 space-y-6">
        <audio
          ref={audioRef}
          src={currentPodcast.audio_url}
          preload="metadata"
        />

        {/* Progress bar */}
        <div className="space-y-2">
          <Slider
            value={[audioRef.current ? (currentTime / audioRef.current.duration) * 100 : 0]}
            onValueChange={handleSeekChange}
            max={100}
            step={0.1}
            className="cursor-pointer"
          />
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(currentPodcast.duration)}</span>
          </div>
        </div>

        {/* Main controls */}
        <div className="flex items-center justify-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => skip(-SKIP_TIME)}
          >
            <SkipBack className="h-5 w-5" />
          </Button>

          <Button
            variant="outline"
            size="icon"
            className="h-12 w-12"
            onClick={togglePlayPause}
          >
            {isPlaying ? (
              <Pause className="h-6 w-6" />
            ) : (
              <Play className="h-6 w-6" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => skip(SKIP_TIME)}
          >
            <SkipForward className="h-5 w-5" />
          </Button>
        </div>

        {/* Additional controls */}
        <div className="flex items-center gap-4">
          {/* Volume control */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleVolumeChange(volume === 0 ? [100] : [0])}
            >
              {volume === 0 ? (
                <VolumeX className="h-4 w-4" />
              ) : volume < 0.5 ? (
                <Volume1 className="h-4 w-4" />
              ) : (
                <Volume2 className="h-4 w-4" />
              )}
            </Button>
            <Slider
              value={[volume * 100]}
              onValueChange={handleVolumeChange}
              max={100}
              step={1}
              className="w-24"
            />
          </div>

          <div className="flex-1" />

          {/* Playback speed */}
          <div className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
            <select
              value={playbackRate}
              onChange={(e) => setPlaybackRate(parseFloat(e.target.value))}
              className="bg-background text-sm p-1 rounded border"
            >
              {PLAYBACK_SPEEDS.map((speed) => (
                <option key={speed} value={speed}>
                  {speed}x
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}