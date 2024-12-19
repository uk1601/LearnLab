'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card } from '@/components/ui/card';
import { useFileStore } from '@/store/file-store';
import { useToast } from '@/hooks/use-toast';
import { API_ROUTES } from '@/config';
import { fetchClient } from '@/lib/api/fetch-client';
import { useRouter } from 'next/navigation';

export function FileUploader() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const addFile = useFileStore((state) => state.addFile);
  const { toast } = useToast();
  const router = useRouter();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 95) {
            clearInterval(interval);
            return 95;
          }
          return prev + 5;
        });
      }, 100);

      const response = await fetchClient(API_ROUTES.files.upload, {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);
      setProgress(100);

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth');
          return;
        }
        throw new Error('Upload failed');
      }

      const data = await response.json();
      addFile(data);
      toast({
        title: "Success",
        description: "File uploaded successfully",
      });
      router.push(`/dashboard/`);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to upload file" + error.message,
      });
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }, [addFile, toast, router]);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    noClick: true,
    multiple: false,
  });

  return (
    <Card
      className="relative border-2 border-dashed"
      {...getRootProps()}
    >
      <div className="p-6 flex flex-col items-center justify-center space-y-4">
        <input {...getInputProps()} />
        <div className="rounded-full p-3 bg-primary/10">
          <Upload className="h-6 w-6 text-primary" />
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold">
            {isDragActive ? "Drop the file here" : "Upload a file"}
          </h3>
          <p className="text-sm text-muted-foreground">
            Drag and drop your file here or click to browse
          </p>
        </div>
        <Button
          onClick={open}
          variant="outline"
          disabled={uploading}
        >
          Choose File
        </Button>
        {uploading && (
          <div className="w-full space-y-2">
            <Progress value={progress} />
            <p className="text-sm text-center text-muted-foreground">
              Uploading... {progress}%
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}