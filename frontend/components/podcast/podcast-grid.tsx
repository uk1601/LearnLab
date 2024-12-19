'use client';

import { useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { usePodcastStore } from '@/store/podcast-store';
import { Play, Pause, Clock, BarChart2 } from 'lucide-react';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';
import { useRouter } from 'next/navigation';

export function PodcastGrid() {
  const { toast } = useToast();
  const router = useRouter();
  
  const { 
    podcasts, 
    setPodcasts,
    currentPodcast,
    setCurrentPodcast,
    isPlaying,
    setIsPlaying,
    updateProgress
  } = usePodcastStore();

  useEffect(() => {
    const fetchPodcasts = async () => {
      try {
        const response = await fetchClient(`${API_ROUTES.podcasts.base}`);
        
        if (!response.ok) {
          if (response.status === 401) {
            router.push('/auth');
            return;
          }
          throw new Error('Failed to fetch podcasts');
        }
        
        const data = await response.json();
        setPodcasts(data);
      } catch (error) {
        console.error('Failed to fetch podcasts:', error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load podcasts",
        });
      }
    };

    fetchPodcasts();
  }, [setPodcasts, toast, router]);

  const handlePlayPause = async (podcast: typeof podcasts[0]) => {
    if (currentPodcast?.id === podcast.id) {
      setIsPlaying(!isPlaying);
    } else {
      try {
        const response = await fetchClient(`${API_ROUTES.podcasts.base}/${podcast.id}`);
        if (!response.ok) throw new Error('Failed to fetch podcast details');
        
        const podcastDetails = await response.json();
        setCurrentPodcast(podcastDetails);
        setIsPlaying(true);
      } catch (error) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to play podcast",
        });
      }
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    }
    return `${minutes}m`;
  };

  if (!podcasts || podcasts.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-40">
          <p className="text-muted-foreground">
            No podcasts found. Upload a podcast to get started.
          </p>
        </CardContent>
      </Card>
    );
  }
  if(!podcasts){
    return (<></>)
  }
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {podcasts.map((podcast) => (
        <Card key={podcast.id} variant="outline" className="hover:shadow-md transition-shadow">
          <CardHeader>
            <CardTitle className="text-lg line-clamp-1">{podcast.title}</CardTitle>
            {podcast.description && (
              <CardDescription className="line-clamp-2">
                {podcast.description}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                {formatDuration(podcast.duration)}
              </div>
              <div className="flex items-center gap-2">
                <BarChart2 className="h-4 w-4" />
                {`${Math.round(podcast.current_progress)}% Complete`}
              </div>
            </div>

            <Progress 
              value={podcast.current_progress} 
              className="h-2"
            />

            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => handlePlayPause(podcast)}
            >
              {currentPodcast?.id === podcast.id && isPlaying ? (
                <>
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Play
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}