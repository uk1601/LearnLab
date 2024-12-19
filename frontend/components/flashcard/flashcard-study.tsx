'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Flashcard } from "@/store/flashcard-store";
import { Loader2, ChevronLeft } from 'lucide-react';

interface FlashcardStudyProps {
  card: Flashcard;
  totalCards: number;
  currentIndex: number;
  isSubmitting?: boolean;
  onReview: (quality: number) => void;
  onExit: () => void;
}

export function FlashcardStudy({ 
  card, 
  totalCards, 
  currentIndex,
  isSubmitting,
  onReview,
  onExit 
}: FlashcardStudyProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [hasRevealed, setHasRevealed] = useState(false);

  // Reset states when card changes
  useEffect(() => {
    setIsFlipped(false);
    setHasRevealed(false);
  }, [card]); // Dependency on card ensures this runs when card changes

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
    if (!hasRevealed) {
      setHasRevealed(true);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button 
          variant="ghost" 
          className="gap-2"
          onClick={onExit}
        >
          <ChevronLeft className="h-4 w-4" />
          Exit Session
        </Button>
        <div className="text-sm text-muted-foreground">
          Card {currentIndex + 1} of {totalCards}
        </div>
      </div>

      <Progress value={(currentIndex / totalCards) * 100} />

      <div className="relative min-h-[400px]">
        <Card 
          className={`min-h-[400px] cursor-pointer transition-all duration-300 ${
            isFlipped ? 'rotate-y-180' : ''
          }`} 
          onClick={handleFlip}
        >
          <div className={`absolute w-full h-full backface-hidden ${
            !isFlipped ? 'block' : 'hidden'
          }`}>
            <CardHeader>
              <CardTitle>Question</CardTitle>
              <CardDescription>Click to reveal answer</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-center p-6 text-lg">
              {card.front_content}
            </CardContent>
          </div>

          <div className={`absolute w-full h-full backface-hidden ${
            isFlipped ? 'block' : 'hidden'
          }`}>
            <CardHeader>
              <CardTitle>Answer</CardTitle>
              <CardDescription>Click to see question</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-center p-6 text-lg">
              {card.back_content}
            </CardContent>
          </div>
        </Card>
      </div>

      {hasRevealed && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">How well did you know this?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-5 gap-2">
              {[1, 2, 3, 4, 5].map((quality) => (
                <Button
                  key={quality}
                  onClick={() => onReview(quality)}
                  disabled={isSubmitting}
                  variant={quality <= 2 ? "destructive" : quality >= 4 ? "default" : "secondary"}
                >
                  {isSubmitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    quality
                  )}
                </Button>
              ))}
            </div>
          </CardContent>
          <CardFooter className="text-xs text-muted-foreground text-center">
            1 = Didn&apos;t know it • 3 = Somewhat knew it • 5 = Knew it perfectly
          </CardFooter>
        </Card>
      )}
    </div>
  );
}