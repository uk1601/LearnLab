// app/dashboard/[fileId]/view-pdf/page.tsx
'use client';

import { FileLayout } from "@/components/layout/file-layout";
import { useFileStore } from "@/store/file-store";
import { PDFViewer } from '@/components/file/pdf-viewer';
import { use } from 'react';
type Params = Promise<{ fileId: string }>;
interface PDFViewerPageProps {
  params: Params
}
import { ErrorBoundary } from 'react-error-boundary';
export default function PDFViewerPage({ params }: PDFViewerPageProps) {
  const unwrappedParams = use(params);
  const { selectedFile } = useFileStore();

  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <FileLayout fileId={unwrappedParams.fileId}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {selectedFile?.filename || 'View PDF'}
            </h1>
            <p className="text-muted-foreground">
              Read and interact with your document
            </p>
          </div>

          <PDFViewer file={selectedFile!} />
        </div>
      </FileLayout>
    </ErrorBoundary>
  );
}