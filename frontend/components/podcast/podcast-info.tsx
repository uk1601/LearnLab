'use client';

import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { usePodcastStore } from '@/store/podcast-store';
import { 
  Clock, 
  Play, 
  BarChart2, 
  BookOpen,
  ArrowUpRight,
  Activity,
  Users,
  PlayCircle
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import { useEffect } from 'react';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';
import { useToast } from "@/hooks/use-toast";

export function PodcastInfo() {
  const { toast } = useToast();
  const { currentPodcast, analytics, updateAnalytics } = usePodcastStore();

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!currentPodcast) return;

      try {
        const response = await fetchClient(`${API_ROUTES.podcasts.base}/${currentPodcast.id}/analytics`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const data = await response.json();
        updateAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load podcast analytics",
        });
      }
    };

    fetchAnalytics();
  }, [currentPodcast, updateAnalytics, toast]);

  if (!currentPodcast) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Podcast Selected</CardTitle>
          <CardDescription>
            Select a podcast to view its details and analytics
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
  };

  const formatSeconds = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="space-y-1">
          <CardTitle>{currentPodcast.title}</CardTitle>
          {currentPodcast.description && (
            <CardDescription>{currentPodcast.description}</CardDescription>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Progress Section */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="font-medium">{Math.round(currentPodcast.current_progress)}%</span>
          </div>
          <Progress value={currentPodcast.current_progress} className="h-2" />
        </div>

        <Separator />

        {/* Main Stats */}
        <div className="grid grid-cols-2 gap-4">
          {/* Duration Card */}
          <Card className="bg-muted">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <Badge variant="secondary">Duration</Badge>
              </div>
              <p className="mt-2 text-2xl font-bold">
                {formatDuration(currentPodcast.duration)}
              </p>
            </CardContent>
          </Card>

          {/* Current Speed Card */}
          <Card className="bg-muted">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <PlayCircle className="h-4 w-4 text-muted-foreground" />
                <Badge variant="secondary">Speed</Badge>
              </div>
              <p className="mt-2 text-2xl font-bold">
                {currentPodcast.current_speed}x
              </p>
            </CardContent>
          </Card>
        </div>

        {analytics && (
          <>
            <Separator />

            {/* Analytics Section */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold">Learning Analytics</h4>
              <div className="grid grid-cols-2 gap-4">
                {/* Total Time */}
                <Card className="bg-muted">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Time Spent</span>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <p className="text-lg font-semibold">
                        {formatDuration(analytics.total_time_listened)}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Sessions */}
                <Card className="bg-muted">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Sessions</span>
                        <Users className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <p className="text-lg font-semibold">
                        {analytics.number_of_sessions}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Average Speed */}
                <Card className="bg-muted">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Avg Speed</span>
                        <Play className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <p className="text-lg font-semibold">
                        {analytics.average_speed.toFixed(1)}x
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Completion Rate */}
                <Card className="bg-muted">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Completion</span>
                        <BarChart2 className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <p className="text-lg font-semibold">
                        {Math.round(analytics.completion_rate * 100)}%
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <Separator />

            {/* Additional Metrics */}
            {analytics.engagement_score !== undefined && (
              <div className="space-y-4">
                <h4 className="text-sm font-semibold">Engagement Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Engagement Score</span>
                    <span className="font-medium">{analytics.engagement_score.toFixed(1)}</span>
                  </div>
                  {analytics.unique_listeners && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Unique Listeners</span>
                      <span className="font-medium">{analytics.unique_listeners}</span>
                    </div>
                  )}
                  {analytics.total_plays && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Total Plays</span>
                      <span className="font-medium">{analytics.total_plays}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        <Separator />

        {/* Metadata */}
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            <span>Created {formatDistanceToNow(new Date(currentPodcast.created_at), { addSuffix: true })}</span>
          </div>
          <div className="flex items-center gap-1">
            <ArrowUpRight className="h-4 w-4" />
            <span>Last updated {formatDistanceToNow(new Date(currentPodcast.updated_at), { addSuffix: true })}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}