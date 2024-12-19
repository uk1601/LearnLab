'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue, 
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Music, FileText } from 'lucide-react';
import { usePodcastStore, Podcast } from '@/store/podcast-store';
import { useFileStore } from '@/store/file-store';
import { useRouter } from 'next/navigation';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';

// Validation constants
const MAX_AUDIO_SIZE = 100 * 1024 * 1024; // 100MB
const MAX_TRANSCRIPT_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_AUDIO_TYPES = {
  'audio/mp3': ['.mp3'],
  'audio/mpeg': ['.mp3'],
  'audio/wav': ['.wav'],
  'audio/m4a': ['.m4a']
};
const ALLOWED_TRANSCRIPT_TYPES = {
  'text/plain': ['.txt'],
  'text/vtt': ['.vtt']
};

export function PodcastUploader() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const { toast } = useToast();
  const setPodcasts = usePodcastStore((state) => state.setPodcasts);
  const { files, setFiles } = useFileStore();
  const router = useRouter();

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetchClient(`${API_ROUTES.files.list}`);
        
        if (!response.ok) {
          if (response.status === 401) {
            router.push('/auth');
            return;
          }
          throw new Error('Failed to fetch files');
        }
        
        const data = await response.json();
        setFiles(data);
      } catch (error) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to fetch source files",
        });
      }
    };

    fetchFiles();
  }, [setFiles, toast, router]);

  const validateFile = (file: File, maxSize: number, allowedTypes: Record<string, string[]>) => {
    if (file.size > maxSize) {
      throw new Error(`File size exceeds ${maxSize / (1024 * 1024)}MB limit`);
    }
    
    const isValidType = Object.keys(allowedTypes).includes(file.type);
    if (!isValidType) {
      throw new Error(`Invalid file type. Allowed types: ${Object.values(allowedTypes).flat().join(', ')}`);
    }
  };

  const onAudioDrop = useCallback((acceptedFiles: File[]) => {
    try {
      const file = acceptedFiles[0];
      validateFile(file, MAX_AUDIO_SIZE, ALLOWED_AUDIO_TYPES);
      setAudioFile(file);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Invalid Audio File",
        description: error instanceof Error ? error.message : "Failed to process audio file",
      });
    }
  }, [toast]);

  const onTranscriptDrop = useCallback((acceptedFiles: File[]) => {
    try {
      const file = acceptedFiles[0];
      validateFile(file, MAX_TRANSCRIPT_SIZE, ALLOWED_TRANSCRIPT_TYPES);
      setTranscriptFile(file);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Invalid Transcript File",
        description: error instanceof Error ? error.message : "Failed to process transcript file",
      });
    }
  }, [toast]);

  const { getRootProps: getAudioRootProps, getInputProps: getAudioInputProps } = useDropzone({
    onDrop: onAudioDrop,
    accept: ALLOWED_AUDIO_TYPES,
    multiple: false,
    disabled: uploading
  });

  const { getRootProps: getTranscriptRootProps, getInputProps: getTranscriptInputProps } = useDropzone({
    onDrop: onTranscriptDrop,
    accept: ALLOWED_TRANSCRIPT_TYPES,
    multiple: false,
    disabled: uploading
  });

  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          return 95;
        }
        return prev + 5;
      });
    }, 500);
    return interval;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title || !audioFile || !transcriptFile || !selectedFileId) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please provide all required fields including source file",
      });
      return;
    }

    setUploading(true);
    const progressInterval = simulateProgress();

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description || '');
      formData.append('file_id', selectedFileId);
      formData.append('audio_file', audioFile);
      formData.append('transcript_file', transcriptFile);

      const response = await fetchClient(`${API_ROUTES.podcasts.base}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setPodcasts([...usePodcastStore.getState().podcasts, data as Podcast]);
      setProgress(100);

      toast({
        title: "Success",
        description: "Podcast created successfully",
      });

      // Reset form
      setTitle('');
      setDescription('');
      setAudioFile(null);
      setTranscriptFile(null);
      setSelectedFileId(null);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create podcast",
      });
    } finally {
      clearInterval(progressInterval);
      setUploading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>Upload New Podcast</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Selection */}
          <div className="space-y-2">
            <Label>Source File</Label>
            <Select
              value={selectedFileId || ""}
              onValueChange={(value) => setSelectedFileId(value)}
              disabled={uploading}
            >
              <SelectTrigger className="bg-background">
                <SelectValue placeholder="Select source file" />
              </SelectTrigger>
              <SelectContent>
                {files.map((file) => (
                  <SelectItem
                    key={file.id}
                    value={file.id}
                  >
                    {file.filename}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={uploading}
              placeholder="Enter podcast title"
              className="bg-background"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={uploading}
              placeholder="Enter podcast description"
              className="bg-background"
            />
          </div>

          {/* File Upload Dropzones */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Audio Upload */}
            <div className="space-y-2">
              <Label>Audio File</Label>
              <div 
                {...getAudioRootProps()} 
                className={`
                  border-2 border-dashed rounded-lg p-6 
                  cursor-pointer transition-colors
                  ${audioFile ? 'border-primary bg-primary/5' : 'border-border'}
                  ${uploading ? 'cursor-not-allowed opacity-50' : 'hover:border-primary/50'}
                `}
              >
                <input {...getAudioInputProps()} />
                <div className="flex flex-col items-center justify-center space-y-2 text-center">
                  <Music className="h-8 w-8 text-muted-foreground" />
                  <div className="text-sm text-muted-foreground">
                    {audioFile ? audioFile.name : 'Drop audio file or click to select'}
                  </div>
                </div>
              </div>
            </div>

            {/* Transcript Upload */}
            <div className="space-y-2">
              <Label>Transcript File</Label>
              <div 
                {...getTranscriptRootProps()} 
                className={`
                  border-2 border-dashed rounded-lg p-6 
                  cursor-pointer transition-colors
                  ${transcriptFile ? 'border-primary bg-primary/5' : 'border-border'}
                  ${uploading ? 'cursor-not-allowed opacity-50' : 'hover:border-primary/50'}
                `}
              >
                <input {...getTranscriptInputProps()} />
                <div className="flex flex-col items-center justify-center space-y-2 text-center">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                  <div className="text-sm text-muted-foreground">
                    {transcriptFile ? transcriptFile.name : 'Drop transcript file or click to select'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="space-y-2">
              <Progress value={progress} />
              <p className="text-sm text-center text-muted-foreground">
                Uploading... {progress}%
              </p>
            </div>
          )}

          {/* Submit Button */}
          <Button 
            type="submit"
            className="w-full"
            disabled={!title || !audioFile || !transcriptFile || !selectedFileId || uploading}
          >
            {uploading ? 'Uploading...' : 'Create Podcast'}
          </Button>
        </CardContent>
      </Card>
    </form>
  );
}