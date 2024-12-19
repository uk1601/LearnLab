'use client';
import { ErrorBoundary, ErrorBoundaryPropsWithFallback } from 'react-error-boundary';
import { FileUploader, FileGrid, FileSelector, FileDetails } from "@/components/file";
import { Separator } from "@/components/ui/separator";


export default function FilesPage() {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>

      <div className="container-base space-y-6 py-8">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Files</h2>
          <p className="text-muted-foreground">
            Manage your files and documents
          </p>
        </div>

        <Separator />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <FileUploader />
            <FileGrid />
          </div>

          <div className="space-y-6">
            <FileSelector />
            <FileDetails />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}