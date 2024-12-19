'use client';

import { useAuth } from "@/components/providers/auth-provider";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileGrid } from "@/components/file";
import { Button } from "@/components/ui/button";
import { Plus, Upload } from "lucide-react";
import { useRouter } from "next/navigation";
import { ErrorBoundary } from 'react-error-boundary';




export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                Welcome back{user?.full_name ? `, ${user.full_name}` : ''}
              </h1>
              <p className="text-muted-foreground">
                Manage your files and learning materials
              </p>
            </div>
            <Button
              className="gap-2"
              onClick={() => router.push('/dashboard/upload')}
            >
              <Upload className="h-4 w-4" />
              Upload File
            </Button>
          </div>

          {/* Files Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold tracking-tight">Your Files</h2>
            </div>
            <FileGrid />
          </div>
        </div>
      </DashboardLayout>
    </ErrorBoundary>
  );
}