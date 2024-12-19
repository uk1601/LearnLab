'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { LayoutGrid, List } from 'lucide-react';
import { PodcastGrid } from './podcast-grid';
import { PodcastList } from './podcast-list';
import { usePodcastStore } from '@/store/podcast-store';

export function PodcastViewer() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const podcastCount = usePodcastStore((state) => state.podcasts.length);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {podcastCount} podcast{podcastCount !== 1 ? 's' : ''} available
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <LayoutGrid className="h-4 w-4 mr-2" />
            Grid
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4 mr-2" />
            List
          </Button>
        </div>
      </div>

      <Separator />

      {viewMode === 'grid' ? <PodcastGrid /> : <PodcastList />}
    </div>
  );
}