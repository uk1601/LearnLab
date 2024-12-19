'use client';

import { useFileStore } from "@/store/file-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { format } from "date-fns";

export function FileDetails() {
  const selectedFile = useFileStore((state) => state.selectedFile);

  if (!selectedFile) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No File Selected</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select a file to view its details
          </p>
        </CardContent>
      </Card>
    );
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>File Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h4 className="font-medium">Filename</h4>
          <p className="text-sm text-muted-foreground">{selectedFile.filename}</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Size</h4>
          <p className="text-sm text-muted-foreground">
            {formatFileSize(selectedFile.file_size)}
          </p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Type</h4>
          <p className="text-sm text-muted-foreground">{selectedFile.mime_type}</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Uploaded</h4>
          <p className="text-sm text-muted-foreground">
            {format(new Date(selectedFile.created_at), 'PPpp')}
          </p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Last Modified</h4>
          <p className="text-sm text-muted-foreground">
            {format(new Date(selectedFile.updated_at), 'PPpp')}
          </p>
        </div>

        <Button 
          className="w-full"
          onClick={() => window.open(selectedFile.download_url, '_blank')}
        >
          <Download className="h-4 w-4 mr-2" />
          Download File
        </Button>
      </CardContent>
    </Card>
  );
}