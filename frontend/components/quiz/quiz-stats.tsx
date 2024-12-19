'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, CheckCircle2, Trophy, Target } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Quiz } from "@/store/quiz-store";

interface QuizStatsProps {
  quizzes: Quiz[];
  isLoading?: boolean;
}

export function QuizStats({ quizzes, isLoading }: QuizStatsProps) {
  // Calculate stats
  const totalQuizzes = quizzes.length;
  const totalQuestions = quizzes.reduce((sum, quiz) => sum + quiz.total_questions, 0);
  const totalAttempts = quizzes.reduce((sum, quiz) => sum + quiz.total_attempts, 0);
  const avgScore = quizzes.reduce((sum, quiz) => sum + (quiz.average_score || 0), 0) / totalQuizzes || 0;

  const stats = [
    {
      title: "Total Quizzes",
      value: totalQuizzes,
      icon: Brain
    },
    {
      title: "Total Questions",
      value: totalQuestions,
      icon: Target
    },
    {
      title: "Total Attempts",
      value: totalAttempts,
      icon: CheckCircle2
    },
    {
      title: "Avg. Score",
      value: `${avgScore.toFixed(1)}%`,
      icon: Trophy
    }
  ];

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                <Skeleton className="h-4 w-24" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}