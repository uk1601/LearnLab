'use client';

import { useEffect } from 'react';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { usePodcastStore } from '@/store/podcast-store';
import { Play, Pause, Clock, BarChart2, Calendar } from 'lucide-react';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';
import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';

export function PodcastList() {
  const { toast } = useToast();
  const router = useRouter();
  
  const { 
    podcasts, 
    setPodcasts,
    currentPodcast,
    setCurrentPodcast,
    isPlaying,
    setIsPlaying
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
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Status</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Progress</TableHead>
              <TableHead>Last Updated</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell colSpan={6} className="text-center h-24 text-muted-foreground">
                No podcasts found. Upload a PDF to get started.
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead>Progress</TableHead>
            <TableHead>Last Updated</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {podcasts.map((podcast) => (
            <TableRow key={podcast.id}>
              <TableCell>
                {currentPodcast?.id === podcast.id && isPlaying ? (
                  <div className="bg-primary/10 text-primary rounded-md px-2 py-1 text-xs inline-flex items-center">
                    Playing
                  </div>
                ) : podcast.current_progress > 0 ? (
                  <div className="bg-muted text-muted-foreground rounded-md px-2 py-1 text-xs inline-flex items-center">
                    In Progress
                  </div>
                ) : (
                  <div className="bg-accent/10 text-accent rounded-md px-2 py-1 text-xs inline-flex items-center">
                    New
                  </div>
                )}
              </TableCell>
              <TableCell>
                <div className="flex flex-col">
                  <span className="font-medium">{podcast.title}</span>
                  {podcast.description && (
                    <span className="text-sm text-muted-foreground line-clamp-1">
                      {podcast.description}
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  {formatDuration(podcast.duration)}
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-1">
                  <Progress 
                    value={podcast.current_progress} 
                    className="h-2"
                  />
                  <p className="text-xs text-muted-foreground">
                    {Math.round(podcast.current_progress)}% Complete
                  </p>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span className="text-sm">
                    {formatDistanceToNow(new Date(podcast.updated_at), { addSuffix: true })}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handlePlayPause(podcast)}
                >
                  {currentPodcast?.id === podcast.id && isPlaying ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}