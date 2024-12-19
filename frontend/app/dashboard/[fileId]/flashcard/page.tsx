'use client';

import { useEffect, useState } from 'react';
import { FileLayout } from "@/components/layout/file-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Brain, Clock, Lightbulb, History } from "lucide-react";
import { useFlashcardStore } from "@/store/flashcard-store";
import { FlashcardDeck, FlashcardStudy, FlashcardProgress, CreateDeckDialog } from "@/components/flashcard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from '@/hooks/use-toast';
import { use } from 'react';
import { Button } from '@/components/ui/button';

interface FlashcardPageProps {
  params: Promise<{
    fileId: string;
  }>;
}
type StudyState = 'list' | 'study' | 'complete';

export default function FlashcardPage({ params }: FlashcardPageProps) {
  // Unwrap params using React's `use()`
  const unwrappedParams = use(params);
  const fileId = unwrappedParams.fileId;
  console.log("-------------")
  console.log(fileId)

  const [studyState, setStudyState] = useState<StudyState>('list');
  const { toast } = useToast();
  
  const { 
    decks,
    currentDeck,
    currentCard,
    deckProgress,
    cardsInDeck,
    currentCardIndex,
    isLoading,
    error,
    fetchDecks,
    fetchDeckCards,
    fetchDeckProgress,
    setCurrentDeck,
    submitCardReview,
    resetStudySession,
    studySessionComplete
  } = useFlashcardStore();

  useEffect(() => {
    console.log('Fetching initial decks for file:', fileId);
    fetchDecks(fileId).catch((error) => {
      console.error('Failed to fetch decks:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load flashcard decks"
      });
    });
  }, [fileId, fetchDecks, toast]);

  useEffect(() => {
    // Monitor studySessionComplete state
    if (studySessionComplete) {
      console.log('Study session completed, transitioning to complete state');
      setStudyState('complete');
    }
  }, [studySessionComplete]);

  const handleStartStudy = async (deckId: string) => {
    console.log('Starting study session for deck:', deckId);
    try {
      await fetchDeckCards(deckId);
      await fetchDeckProgress(deckId);
      console.log('Successfully fetched cards and progress, cards:', cardsInDeck.length);
      setStudyState('study');
    } catch (error) {
      console.error('Failed to start study session:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to start study session"
      });
    }
  };

  const handleReview = async (quality: number) => {
    if (!currentCard) {
      console.error('No current card available for review');
      return;
    }
    
    console.log('Submitting review:', { cardId: currentCard.id, quality });
    try {
      await submitCardReview(currentCard.id, quality);
      if (studySessionComplete) {
        console.log('Study session complete, fetching final progress');
        await fetchDeckProgress(currentDeck!.id);
      }
    } catch (error) {
      console.error('Failed to submit review:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to submit review"
      });
    }
  };

  const handleReturnToList = () => {
    console.log('Returning to deck list');
    resetStudySession();
    setStudyState('list');
  };

  console.log('Current state:', { 
    studyState, 
    currentCard, 
    currentDeck,
    cardsInDeck: cardsInDeck.length,
    currentCardIndex 
  });

  const renderContent = () => {
    if (isLoading && studyState === 'list') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="w-full">
              <CardHeader>
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[100px]" />
              </CardContent>
            </Card>
          ))}
        </div>
      );
    }

    switch (studyState) {
      case 'study':
        if (!currentCard || !currentDeck || cardsInDeck.length === 0) {
          console.error('Study state active but missing data:', {
            hasCurrentCard: !!currentCard,
            hasCurrentDeck: !!currentDeck,
            cardsCount: cardsInDeck.length
          });
          
          return (
            <div className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>Failed to load study session</AlertDescription>
              </Alert>
              <Button variant="outline" onClick={handleReturnToList}>
                Return to Decks
              </Button>
            </div>
          );
        }
        return (
          <FlashcardStudy
            card={currentCard}
            totalCards={cardsInDeck.length}
            currentIndex={currentCardIndex}
            isSubmitting={isLoading}
            onReview={handleReview}
            onExit={handleReturnToList}
          />
        );

      case 'complete':
        if (!deckProgress) {
          console.error('Complete state active but no deck progress');
          return null;
        }
        return (
          <FlashcardProgress
            progress={deckProgress}
            onReturn={handleReturnToList}
            onStudyAgain={() => currentDeck && handleStartStudy(currentDeck.id)}
          />
        );

      default:
        return (
          <div className="space-y-6">
            {/* Header with Create Button */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Flashcards</h1>
                <p className="text-muted-foreground">
                  Master concepts through spaced repetition
                </p>
              </div>
              <CreateDeckDialog fileId={fileId} />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Learning Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Cards</CardTitle>
                  <Brain className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {decks.reduce((sum, deck) => sum + (deckProgress?.total_cards || 0), 0)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Due Today</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">0</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Mastered</CardTitle>
                  <Lightbulb className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {decks.reduce((sum, deck) => sum + (deckProgress?.mastered_cards || 0), 0)}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Review Rate</CardTitle>
                  <History className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {Math.round((decks.reduce((sum, deck) => sum + (deckProgress?.mastery_percentage || 0), 0) / (decks.length || 1)))}%
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Decks Grid */}
            <Card>
              <CardHeader>
                <CardTitle>Your Decks</CardTitle>
                <CardDescription>
                  Select a deck to start studying
                </CardDescription>
              </CardHeader>
              <CardContent>
                {decks.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    No decks available. Create your first deck to get started!
                  </div>
                ) : (
                  <ScrollArea className="h-[500px] pr-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {decks.map((deck) => (
                        <FlashcardDeck
                          key={deck.id}
                          deck={deck}
                          progress={deckProgress}
                          onStudy={() => handleStartStudy(deck.id)}
                        />
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </div>
        );
    }
  };

  return <FileLayout fileId={fileId}>{renderContent()}</FileLayout>;
}
