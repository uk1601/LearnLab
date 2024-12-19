'use client';

import { useEffect } from 'react';
import { useRouter } from "next/navigation";
import { FileLayout } from "@/components/layout/file-layout";
import { QuizList, QuizStats } from "@/components/quiz";
import { useQuizStore } from "@/store/quiz-store";
import { useToast } from "@/hooks/use-toast";
import {use} from 'react';
type Params = Promise<{ fileId: string }>;
interface QuizPageProps {
  params: Params
}

export default function QuizPage({ params }: QuizPageProps) {
  const router = useRouter();
  const unwrappedParams = use(params);
  const { toast } = useToast();
  const { 
    quizzes, 
    isLoading, 
    error,
    fetchQuizzes,
    startQuiz
  } = useQuizStore();

  useEffect(() => {
    const loadQuizzes = async () => {
      try {
        await fetchQuizzes(unwrappedParams.fileId);
      } catch (err) {
        toast({
          title: "Error",
          description: "Failed to load quizzes. Please try again.",
          variant: "destructive"
        });
      }
    };

    loadQuizzes();
  }, [unwrappedParams.fileId, fetchQuizzes, toast]);

  const handleSelectQuiz = async (quiz: typeof quizzes[0]) => {
    try {
      await startQuiz(quiz.id);
      // Navigate to quiz attempt page
      router.push(`/dashboard/${unwrappedParams.fileId}/quiz/${quiz.id}/attempt`);
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to start quiz. Please try again.",
        variant: "destructive"
      });
    }
  };

  return (
    <FileLayout fileId={unwrappedParams.fileId}>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quizzes</h1>
          <p className="text-muted-foreground">
            Test your knowledge and track your progress
          </p>
        </div>

        {/* Stats */}
        <QuizStats 
          quizzes={quizzes}
          isLoading={isLoading}
        />

        {/* Quiz List */}
        <QuizList 
          quizzes={quizzes}
          isLoading={isLoading}
          onSelectQuiz={handleSelectQuiz}
        />

        {error && (
          <div className="text-center text-destructive">
            {error}
          </div>
        )}
      </div>
    </FileLayout>
  );
}