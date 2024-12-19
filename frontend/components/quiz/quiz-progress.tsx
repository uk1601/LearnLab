'use client';

import { Progress } from "@/components/ui/progress";
import { QuestionResponse } from "@/store/quiz-store";
import { cn } from "@/lib/utils";

interface QuizProgressProps {
  currentQuestionIndex: number;
  totalQuestions: number;
  responses: Record<string, QuestionResponse>;
  className?: string;
}

export function QuizProgress({ 
  currentQuestionIndex, 
  totalQuestions,
  responses,
  className 
}: QuizProgressProps) {
  const progress = (currentQuestionIndex / totalQuestions) * 100;
  const answeredQuestions = Object.keys(responses).length;
  
  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex justify-between text-sm text-muted-foreground">
        <span>
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </span>
        <span>
          {answeredQuestions} Answered
        </span>
      </div>
      <Progress value={progress} className="h-2" />
    </div>
  );
}