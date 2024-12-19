'use client';

import { useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useFileStore } from '@/store/file-store';
import { Download, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useToast } from '@/hooks/use-toast';
import { API_ROUTES } from '@/config';
import { fetchClient } from '@/lib/api/fetch-client';
import { useRouter } from 'next/navigation';
import { FileResponse } from '@/types/file';

export function FileGrid() {
  const { files, setFiles, removeFile, setSelectedFile } = useFileStore();
  const { toast } = useToast();
  const router = useRouter();
  const handleCardClick = (file: FileResponse) => {
    setSelectedFile(file)
    router.push(`/dashboard/${file.id}`);
  };

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetchClient(API_ROUTES.files.list);
        
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
          description: "Failed to fetch files",
        });
      }
    };

    fetchFiles();
  }, [setFiles, toast, router]);

  const handleDelete = async (fileId: string) => {
    try {
      const response = await fetchClient(API_ROUTES.files.delete(fileId), {
        method: 'DELETE',
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/auth');
          return;
        }
        throw new Error('Failed to delete file');
      }

      removeFile(fileId);
      setSelectedFile(null);
      toast({
        title: "Success",
        description: "File deleted successfully",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete file",
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  type VarientType = "default" | "destructive" | "primary" | "secondary" | "accent" | "warning" | "success" | "ghost" | "outline" | null | undefined
  // Array of card variants from our design system
  const cardVariants:VarientType[] = [
    'primary',
    'secondary',
    'accent',
    'warning',
    'success'
  ];

  if (files.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-muted-foreground">
          Upload PDFs to explore interactive and fun learning modes
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {files.map((file, index) => (
        <Card 
          key={file.id} 
          className="hover:shadow-md transition-shadow cursor-pointer border border-black"
          variant={cardVariants[index % cardVariants.length]}
          onClick={() => handleCardClick(file)}
        >
          <CardHeader>
            <CardTitle className="text-lg truncate">
              {file.filename}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Size: {formatFileSize(file.file_size)}
            </p>
            <p className="text-sm text-muted-foreground">
              Uploaded: {formatDistanceToNow(new Date(file.created_at))} ago
            </p>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                window.open(file.download_url, '_blank');
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(file.id);
              }}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}