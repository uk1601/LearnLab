'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Brain } from "lucide-react";
import { useRouter } from "next/navigation";
import { Deck, DeckProgress } from "@/store/flashcard-store";

interface FlashcardDeckProps {
  deck: Deck;
  progress?: DeckProgress | null;
  onStudy: () => void;
}

export function FlashcardDeck({ deck, progress, onStudy }: FlashcardDeckProps) {
  const router = useRouter();

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-lg font-semibold">{deck.title}</CardTitle>
        <Brain className="h-5 w-5 text-muted-foreground" />
      </CardHeader>
      <CardContent className="space-y-4">
        {deck.description && (
          <CardDescription>
            {deck.description}
          </CardDescription>
        )}

        {progress && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Mastery</span>
              <span className="text-muted-foreground">
                {progress.mastery_percentage.toFixed(1)}%
              </span>
            </div>
            <Progress value={progress.mastery_percentage} />
            
            <div className="grid grid-cols-3 gap-2 text-sm pt-2">
              <div>
                <p className="text-muted-foreground">Total</p>
                <p className="font-medium">{progress.total_cards}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Learning</p>
                <p className="font-medium">{progress.learning_cards}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Mastered</p>
                <p className="font-medium">{progress.mastered_cards}</p>
              </div>
            </div>
          </div>
        )}

        <div className="pt-4">
          <Button 
            className="w-full"
            onClick={onStudy}
          >
            Study Now
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}