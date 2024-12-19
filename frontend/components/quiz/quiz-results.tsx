'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Quiz, QuizAttempt } from "@/store/quiz-store";
import { Trophy, Clock, Target, ArrowRight } from "lucide-react";
import { formatDistance } from "date-fns";

interface QuizResultsProps {
  quiz: Quiz;
  attempt: QuizAttempt;
  onViewAnswers: () => void;
  onRetry: () => void;
  onReturn: () => void;
}

export function QuizResults({ quiz, attempt, onViewAnswers, onRetry, onReturn }: QuizResultsProps) {
  const score = attempt.score || 0;
  const duration = attempt.end_time && attempt.start_time
    ? new Date(attempt.end_time).getTime() - new Date(attempt.start_time).getTime()
    : 0;

  return (
    <div className="space-y-8">
      {/* Score Card */}
      <Card className="text-center">
        <CardHeader>
          <CardTitle className="text-2xl">Quiz Complete!</CardTitle>
          <CardDescription>
            Here's how you did on {quiz.title}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Score Circle */}
          <div className="relative w-32 h-32 mx-auto">
            <div className="absolute inset-0 flex items-center justify-center">
              <div>
                <div className="text-4xl font-bold">
                  {Math.round(score)}%
                </div>
                <div className="text-sm text-muted-foreground">Score</div>
              </div>
            </div>
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="60"
                className="stroke-current text-muted stroke-[8]"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="60"
                className="stroke-current text-primary stroke-[8]"
                fill="none"
                strokeDasharray={2 * Math.PI * 60}
                strokeDashoffset={2 * Math.PI * 60 * (1 - score / 100)}
                strokeLinecap="round"
              />
            </svg>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1">
              <div className="flex items-center justify-center text-muted-foreground">
                <Target className="w-4 h-4 mr-1" />
                Questions
              </div>
              <div className="text-2xl font-semibold">
                {quiz.total_questions}
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-center text-muted-foreground">
                <Trophy className="w-4 h-4 mr-1" />
                Best Score
              </div>
              <div className="text-2xl font-semibold">
                {quiz.highest_score ? `${Math.round(quiz.highest_score)}%` : 'N/A'}
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-center text-muted-foreground">
                <Clock className="w-4 h-4 mr-1" />
                Time
              </div>
              <div className="text-2xl font-semibold">
                {formatDistance(0, duration, { includeSeconds: true })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-center gap-4">
        <Button 
          variant="outline"
          onClick={onRetry}
        >
          Try Again
        </Button>
        <Button 
          variant="secondary"
          onClick={onReturn}
        >
          Back to Quizzes
        </Button>
        <Button 
          onClick={onViewAnswers}
          className="gap-2"
        >
          Review Answers
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}