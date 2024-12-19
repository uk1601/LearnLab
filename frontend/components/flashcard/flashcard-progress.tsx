'use client';

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { DeckProgress } from "@/store/flashcard-store";
import { CheckCircle } from "lucide-react";

interface FlashcardProgressProps {
  progress: DeckProgress;
  onReturn: () => void;
  onStudyAgain: () => void;
}

export function FlashcardProgress({ 
  progress,
  onReturn,
  onStudyAgain
}: FlashcardProgressProps) {
  return (
    <div className="space-y-6">
      <Card className="border-success">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-success" />
          </div>
          <CardTitle className="text-center">Session Complete!</CardTitle>
          <CardDescription className="text-center">
            Great job on completing your study session
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Mastery</span>
              <span className="text-muted-foreground">
                {progress.mastery_percentage.toFixed(1)}%
              </span>
            </div>
            <Progress value={progress.mastery_percentage} />
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <Card>
              <CardHeader className="py-2">
                <CardTitle className="text-2xl font-bold">
                  {progress.total_cards}
                </CardTitle>
                <CardDescription>Total Cards</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="py-2">
                <CardTitle className="text-2xl font-bold">
                  {progress.learning_cards}
                </CardTitle>
                <CardDescription>Learning</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="py-2">
                <CardTitle className="text-2xl font-bold">
                  {progress.mastered_cards}
                </CardTitle>
                <CardDescription>Mastered</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          <Button 
            className="w-full" 
            variant="default"
            onClick={onStudyAgain}
          >
            Study Again
          </Button>
          <Button 
            className="w-full" 
            variant="outline"
            onClick={onReturn}
          >
            Return to Decks
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}