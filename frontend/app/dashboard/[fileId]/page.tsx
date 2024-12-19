'use client';

import { FileLayout } from "@/components/layout/file-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useFileStore } from "@/store/file-store";
import { useEffect } from "react";
import { Headphones, BrainCircuit, Car } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { use } from "react";
import { usePodcastStore } from "@/store/podcast-store";
import { useQuizStore } from "@/store/quiz-store";
import { useFlashcardStore } from "@/store/flashcard-store";
import { ErrorBoundary } from 'react-error-boundary';

type Params = Promise<{ fileId: string }>

interface FilePageProps {
  params: Params;
}

export default function FilePage({ params }: FilePageProps) {
  // Unwrap the params Promise using React.use()
  const resolvedParams = use(params);
  const fileId = resolvedParams.fileId;

  const router = useRouter();
  const { selectedFile } = useFileStore();
  const { podcasts } = usePodcastStore();
  const { quizzes } = useQuizStore();
  const { decks, fetchDecks } = useFlashcardStore();

  // Compute podcast statistics
  const podcastStats = {
    total: podcasts.length,
    completed: podcasts.filter(p => (p.current_progress || 0) === 100).length,
    inProgress: podcasts.filter(p => (p.current_progress || 0) > 0 && (p.current_progress || 0) < 100).length
  };

  // Compute quiz statistics
  const quizStats = {
    total: quizzes.length,
    attempted: quizzes.filter(q => q.total_attempts > 0).length,
    averageScore: quizzes.length > 0
      ? quizzes.reduce((sum, q) => sum + (q.average_score || 0), 0) / quizzes.length
      : 0
  };

  // Initialize feature cards with real data
  const features = [
    {
      title: "Podcasts",
      icon: Headphones,
      description: `${podcastStats.total} podcast${podcastStats.total !== 1 ? 's' : ''} generated`,
      href: `/dashboard/${fileId}/podcast`,
      stats: [
        { label: "Total", value: podcastStats.total.toString() },
        { label: "Completed", value: podcastStats.completed.toString() },
        { label: "In Progress", value: podcastStats.inProgress.toString() }
      ]
    },
    {
      title: "Quizzes",
      icon: BrainCircuit,
      description: `${quizStats.total} quiz${quizStats.total !== 1 ? 'zes' : ''} created`,
      href: `/dashboard/${fileId}/quiz`,
      stats: [
        { label: "Total", value: quizStats.total.toString() },
        { label: "Attempted", value: quizStats.attempted.toString() },
        { label: "Avg. Score", value: `${Math.round(quizStats.averageScore)}%` }
      ]
    },
    {
      title: "Flashcards",
      icon: Car,
      description: `${decks.length} deck${decks.length !== 1 ? 's' : ''} created`,
      href: `/dashboard/${fileId}/flashcard`,
      stats: [
        { 
          label: "Total Decks", 
          value: decks.length.toString() 
        },
        { 
          label: "Total Cards", 
          value: decks.reduce((sum, deck) => sum + (5), 0).toString() 
        },
        {
          label: "Mastered",
          value: decks.reduce((sum, deck) => sum + (3), 0).toString()
        }
      ]
    }
  ];

  // Fetch data when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        await Promise.all([
          fetchDecks(fileId)
        ]);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [fileId, fetchDecks]);

  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <FileLayout fileId={fileId}>
        <div className="space-y-6">
          {/* File Header */}
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {selectedFile?.filename || 'File Dashboard'}
            </h1>
            <p className="text-muted-foreground">
              View and manage your learning materials
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <Card key={feature.title} className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <CardTitle className="text-sm font-medium">
                    {feature.title}
                  </CardTitle>
                  <feature.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <CardDescription>{feature.description}</CardDescription>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      {feature.stats.map((stat) => (
                        <div key={stat.label}>
                          <p className="text-muted-foreground">{stat.label}</p>
                          <p className="font-medium">{stat.value}</p>
                        </div>
                      ))}
                    </div>
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={() => router.push(feature.href)}
                    >
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </FileLayout>
    </ErrorBoundary>
  );
}