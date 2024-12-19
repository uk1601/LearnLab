'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Question, QuestionResponse } from "@/store/quiz-store";
import { CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface AnswersReviewProps {
  questions: Question[];
  responses: Record<string, QuestionResponse>;
}

export function AnswersReview({ questions, responses }: AnswersReviewProps) {
  const getQuestionContent = (question: Question, response: QuestionResponse) => {
    if ('multiple_choice_options' in question) {
      return (
        <div className="space-y-3">
          {question.multiple_choice_options.map((option) => (
            <div 
              key={option.id}
              className={cn(
                "p-3 rounded-lg border",
                option.is_correct && "bg-success/10 border-success",
                response.response === option.content && !option.is_correct && "bg-destructive/10 border-destructive",
                response.response !== option.content && !option.is_correct && "bg-background"
              )}
            >
              <div className="flex items-center gap-2">
                {option.is_correct && <CheckCircle2 className="w-4 h-4 text-success" />}
                {response.response === option.content && !option.is_correct && 
                  <XCircle className="w-4 h-4 text-destructive" />
                }
                <span>{option.content}</span>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return (
      <div className="space-y-3">
        <div className="p-3 rounded-lg border bg-muted/50">
          <div className="font-medium mb-1">Your Answer:</div>
          <div>{response.response}</div>
        </div>
        <div className="p-3 rounded-lg border bg-success/10 border-success">
          <div className="font-medium mb-1">Correct Answer:</div>
          <div>{question.explanation}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Review Answers</CardTitle>
          <CardDescription>
            Check your answers and review explanations
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="space-y-6">
        {questions.map((question, index) => {
          const response = responses[question.id];
          if (!response) return null;

          return (
            <Card key={question.id}>
              <CardHeader>
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">
                      Question {index + 1}
                    </div>
                    <CardTitle className="text-lg">
                      {question.content}
                    </CardTitle>
                  </div>
                  <Alert 
                    variant={response.is_correct ? "default" : "destructive"}
                    className="w-auto h-auto p-2"
                  >
                    <AlertDescription>
                      {response.is_correct ? "Correct" : "Incorrect"}
                    </AlertDescription>
                  </Alert>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {getQuestionContent(question, response)}

                <div className="bg-muted rounded-lg p-4 mt-4">
                  <div className="font-medium mb-2">Explanation</div>
                  <div className="text-sm text-muted-foreground">
                    {question.explanation}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}