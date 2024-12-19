'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, CheckCircle, XCircle, ArrowRight } from "lucide-react";
import { Question, QuestionWithOptions, QuestionResponse } from "@/store/quiz-store";
import { useQuizStore } from '@/store/quiz-store';

interface QuestionViewProps {
  question: Question;
  response?: QuestionResponse;
  onSubmit: (response: string) => Promise<void>;
  onNext: () => void;
  isLast: boolean;
}

export function QuestionView({ question, response, onSubmit, onNext, isLast }: QuestionViewProps) {
  const [userAnswer, setUserAnswer] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [alreadySubmitted, setAlreadySubmitted] = useState(false);

  const { responses } = useQuizStore();

  // Check for existing response when question changes
  useEffect(() => {
    const existingResponse = responses[question.id];
    if (existingResponse) {
      setUserAnswer(existingResponse.response);
      setShowFeedback(true);
      setAlreadySubmitted(true);
    } else {
      setUserAnswer('');
      setError('');
      setSubmitting(false);
      setShowFeedback(false);
      setAlreadySubmitted(false);
    }
  }, [question.id, responses]);

  const handleSubmit = async () => {
    if (!userAnswer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await onSubmit(userAnswer);
      setShowFeedback(true);
    } catch (err) {
      if (err instanceof Error && err.message.toLowerCase().includes('already')) {
        // Allow navigation but show feedback
        setShowFeedback(true);
        setAlreadySubmitted(true);
      } else {
        setError('Failed to submit answer. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getCorrectAnswer = (question: Question) => {
    if (question.question_type === 'multiple_choice') {
      const correctOption = (question as QuestionWithOptions).multiple_choice_options.find(opt => opt.is_correct);
      return correctOption?.content;
    } else {
      return question.subjective_answer.answer;
    }
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>{question.content}</CardTitle>
        {question.concepts?.length > 0 && (
          <CardDescription>
            Topics: {question.concepts.map(c => c.concept).join(', ')}
          </CardDescription>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Question Input - Only show if not already submitted */}
        {!alreadySubmitted && !showFeedback && (
          <div>
            {question.question_type === 'multiple_choice' ? (
              <RadioGroup
                value={userAnswer}
                onValueChange={setUserAnswer}
                disabled={submitting}
              >
                <div className="space-y-3">
                  {(question as QuestionWithOptions).multiple_choice_options.map((option) => (
                    <div key={option.id} className="flex items-center space-x-2">
                      <RadioGroupItem value={option.content} id={option.id} />
                      <Label 
                        htmlFor={option.id}
                        className="flex-grow cursor-pointer py-2"
                      >
                        {option.content}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            ) : (
              <Textarea
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                placeholder="Enter your answer..."
                disabled={submitting}
                className="min-h-[100px]"
              />
            )}
          </div>
        )}

        {/* Answer Feedback */}
        {(showFeedback || alreadySubmitted) && response && (
          <div className="space-y-4 border rounded-lg p-4">
            <div className="flex items-center gap-2">
              {response.is_correct ? (
                <>
                  <CheckCircle className="h-5 w-5 text-success" />
                  <span className="font-medium text-success">Correct!</span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-destructive" />
                  <span className="font-medium text-destructive">Incorrect</span>
                </>
              )}
            </div>

            <div className="space-y-2">
              <div>
                <span className="font-medium">Your answer:</span>
                <p className="mt-1 text-muted-foreground">{response.response}</p>
              </div>

              {!response.is_correct && (
                <div>
                  <span className="font-medium">Correct answer:</span>
                  <p className="mt-1 text-muted-foreground">
                    {getCorrectAnswer(question)}
                  </p>
                </div>
              )}

              <div>
                <span className="font-medium">Explanation:</span>
                <p className="mt-1 text-muted-foreground">{question.explanation}</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message - with Next button if already submitted */}
        {error && (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
            {alreadySubmitted && (
              <Button 
                onClick={onNext}
                variant="secondary"
                className="gap-2"
              >
                Next Question
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          {!showFeedback && !alreadySubmitted ? (
            <Button
              onClick={handleSubmit}
              disabled={submitting || !userAnswer.trim()}
            >
              Submit Answer
            </Button>
          ) : (
            <Button
              onClick={onNext}
              className="gap-2"
            >
              {isLast ? 'Complete Quiz' : 'Next Question'}
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
