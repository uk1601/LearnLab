'use client';

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";
import { Clock, Brain, CheckCircle2 } from "lucide-react";
import { Quiz } from "@/store/quiz-store";
import { Skeleton } from "@/components/ui/skeleton";

interface QuizListProps {
  quizzes: Quiz[];
  isLoading?: boolean;
  onSelectQuiz: (quiz: Quiz) => void;
}

export function QuizList({ quizzes, isLoading, onSelectQuiz }: QuizListProps) {
  // Array of card variants from our design system
  type VarientType = "default" | "destructive" | "primary" | "secondary" | "accent" | "warning" | "success" | "ghost" | "outline" | null | undefined
  const cardVariants: VarientType[] = [
    'primary',
    'secondary',
    'accent',
    'warning',
    'success'
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-36" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!quizzes.length) {
    return (
      <div className="text-center text-muted-foreground py-8">
        No quizzes available
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {quizzes.map((quiz, index) => (
        <Card 
          key={quiz.id}
          className="hover:shadow-md transition-shadow"
          variant={cardVariants[index % cardVariants.length]}
        >
          <CardHeader>
            <CardTitle className="flex justify-between items-start">
              <span className="text-xl font-semibold">{quiz.title}</span>
              {quiz.average_score && (
                <span className="text-sm font-normal text-muted-foreground">
                  Avg. Score: {quiz.average_score.toFixed(1)}%
                </span>
              )}
            </CardTitle>
            {quiz.description && (
              <CardDescription>{quiz.description}</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <div className="flex items-center">
                <Brain className="h-4 w-4 mr-1" />
                {quiz.total_questions} Questions
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="h-4 w-4 mr-1" />
                {quiz.total_attempts} Attempts
              </div>
              {quiz.last_attempt && (
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  Last attempt {formatDistanceToNow(new Date(quiz.last_attempt))} ago
                </div>
              )}
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full"
              onClick={() => onSelectQuiz(quiz)}
            >
              Start Quiz
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}