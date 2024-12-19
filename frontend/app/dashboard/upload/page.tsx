'use client';

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { FileUploader } from "@/components/file";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { useEffect, useState } from "react";
import { ErrorBoundary } from 'react-error-boundary';
export default function UploadPage() {
  const router = useRouter();
  // const [isLoading, setIsLoading] = useState(true);
  // const [error, setError] = useState<Error | null>(null);

  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <DashboardLayout>
        <div className="space-y-6">
          <Button
            variant="ghost"
            className="gap-2"
            onClick={() => router.back()}
          >
            <ChevronLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>

          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Upload File</CardTitle>
                <CardDescription>
                  Upload your PDF files to start learning with LearnLab
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUploader />
              </CardContent>
            </Card>
          </div>
        </div>
      </DashboardLayout>
    </ErrorBoundary>
  );
}