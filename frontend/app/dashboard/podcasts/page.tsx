'use client';

import { useEffect } from 'react';
import {
  PodcastUploader,
  PodcastViewer,
  PodcastInfo,
  PodcastPlayer,
  PodcastTranscript
} from "@/components/podcast";
import { ErrorBoundary } from 'react-error-boundary';
export default function PodcastsPage() {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <div className="container-base space-y-8 py-8">
        {/* Header Section */}
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Audio Learning</h2>
          <p className="text-muted-foreground">
            Convert PDFs into interactive audio learning experiences
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            <PodcastUploader />
            <PodcastViewer />
          </div>

          {/* Right Column - Info and Analytics */}
          <div className="space-y-6">
            <PodcastInfo />
          </div>
        </div>

        {/* Player and Transcript Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Audio Player */}
          <div className="lg:col-span-2">
            <PodcastPlayer />
          </div>

          {/* Transcript */}
          <div className="lg:col-span-1">
            <PodcastTranscript />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}