'use client';

import { FileLayout } from "@/components/layout/file-layout";
import { PodcastUploader, PodcastViewer, PodcastInfo, PodcastPlayer } from "@/components/podcast";
import {use} from "react";
type Params = Promise<{ fileId: string }>
interface PodcastPageProps {
  params: Params;
}

export default function PodcastPage({ params }: PodcastPageProps) {
  const unwrappedParams = use(params);

  return (
    <FileLayout fileId={unwrappedParams.fileId}>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Podcasts</h1>
          <p className="text-muted-foreground">
            Convert your document into audio learning experiences
          </p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            <PodcastViewer />
            {/* Player and Transcript Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Audio Player */}
              <div className="lg:col-span-2">
                <PodcastPlayer />
              </div>

              {/* Transcript */}
              <div className="lg:col-span-1">
              {/* <PodcastTranscript /> */}
              </div>
            </div>
          </div>

          {/* Right Column - Info and Analytics */}
          <div className="space-y-6">
            {/* <PodcastInfo /> */}
            {/* <PodcastTranscript /> */}
          </div>
        </div>


      </div>
    </FileLayout>
  );
}