'use client';

import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { usePodcastStore } from '@/store/podcast-store';
import { Search, Clock } from 'lucide-react';
import { debounce } from 'lodash';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { fetchClient } from '@/lib/api/fetch-client';
import { API_BASE_URL } from '@/config';

interface TranscriptLine {
  startTime: number;
  endTime: number;
  text: string;
}

export function PodcastTranscript() {
  const { currentPodcast, currentTime, setCurrentTime } = usePodcastStore();
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeLineRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);


  // Parse WebVTT format
  const parseVTT = (vttText: string): TranscriptLine[] => {
    const lines: TranscriptLine[] = [];
    const cues = vttText.trim().split('\n\n').slice(1); // Skip WEBVTT header

    cues.forEach(cue => {
      const [timing, ...textLines] = cue.split('\n').filter(Boolean);
      if (!timing) return;

      const [startTimeStr, endTimeStr] = timing.split(' --> ');
      if (!startTimeStr || !endTimeStr) return;

      const startTime = timeToSeconds(startTimeStr.trim());
      const endTime = timeToSeconds(endTimeStr.trim());
      const text = textLines.join(' ').trim();

      if (text) {
        lines.push({ startTime, endTime, text });
      }
    });

    return lines;
  };

  // Parse plain text format
  const parseTextTranscript = (text: string): TranscriptLine[] => {
    if (!currentPodcast) return [];

    // Split into meaningful segments (paragraphs or sentences)
    const segments = text.split(/(?<=[.!?])\s+(?=[A-Z])/).filter(Boolean);
    const avgDuration = currentPodcast.duration / segments.length;

    return segments.map((segment, index) => ({
      startTime: index * avgDuration,
      endTime: (index + 1) * avgDuration,
      text: segment.trim()
    }));
  };

  useEffect(() => {
    const fetchTranscript = async () => {
      try {
        // Simulate fetching transcript data
        const response = await fetchClient(`${API_BASE_URL}/api/transcripts/${currentPodcast}`);
        const data = await response.json();

        if (data.format === 'text') {
          const parsedTranscript = parseTextTranscript(data.transcript);
          setTranscript(parsedTranscript);
        } else if (data.format === 'vtt') {
          const parsedTranscript = parseVTT(data.transcript);
          setTranscript(parsedTranscript);
        } else {
          console.error('Unsupported transcript format');
        }
      } catch (error) {
        console.error('Error fetching transcript:', error);
      }
    };

    fetchTranscript();
  }, [currentPodcast, parseTextTranscript, parseVTT]);
  // Convert VTT timestamp to seconds
  const timeToSeconds = (timeStr: string): number => {
    const [hours, minutes, secondsMs] = timeStr.split(':');
    const [seconds, ms] = secondsMs.split('.');
    return (
      parseInt(hours) * 3600 +
      parseInt(minutes) * 60 +
      parseInt(seconds) +
      (ms ? parseInt(ms) / 1000 : 0)
    );
  };

  // Format seconds to timestamp
  const formatTime = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Auto-scroll to active line
  useEffect(() => {
    if (activeLineRef.current && !searchQuery) {
      activeLineRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }, [currentTime, searchQuery]);

  // Filter and highlight search results
  const getFilteredTranscript = () => {
    if (!searchQuery) return transcript;

    const query = searchQuery.toLowerCase();
    return transcript.filter(line =>
      line.text.toLowerCase().includes(query)
    );
  };

  // Debounced search handler
  const handleSearch = debounce((value: string) => {
    setSearchQuery(value);
  }, 300);

  // Handle click on transcript line
  const handleLineClick = (startTime: number) => {
    setCurrentTime(startTime);
  };

  // Find active line based on current time
  const getActiveLine = (lines: TranscriptLine[]) => {
    return lines.findIndex(
      line => currentTime >= line.startTime && currentTime <= line.endTime
    );
  };

  if (!currentPodcast) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Podcast Selected</CardTitle>
        </CardHeader>
      </Card>
    );
  }

  const filteredTranscript = getFilteredTranscript();
  const activeLine = getActiveLine(transcript);

  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle>Transcript</CardTitle>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search transcript..."
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-8"
          />
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            Loading transcript...
          </div>
        ) : error ? (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : filteredTranscript.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            {searchQuery ? 'No matches found' : 'No transcript available'}
          </div>
        ) : (
          <ScrollArea
            ref={scrollAreaRef}
            className="h-[500px] pr-4"
          >
            <div className="space-y-4">
              {filteredTranscript.map((line, index) => {
                const isActive = !searchQuery && index === activeLine;
                const highlightedText = searchQuery
                  ? line.text.replace(
                    new RegExp(searchQuery, 'gi'),
                    match => `<mark class="bg-accent text-accent-foreground px-1 rounded">${match}</mark>`
                  )
                  : line.text;

                return (
                  <div
                    key={index}
                    ref={isActive ? activeLineRef : null}
                    className={`
                      p-3 rounded-md cursor-pointer transition-colors
                      ${isActive ? 'bg-accent text-accent-foreground' : 'hover:bg-muted'}
                    `}
                    onClick={() => handleLineClick(line.startTime)}
                  >
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                      <Clock className="h-3 w-3" />
                      {formatTime(line.startTime)}
                    </div>
                    <p
                      className="text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: highlightedText }}
                    />
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}