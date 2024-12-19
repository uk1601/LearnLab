'use client';

import { FileLayout } from "@/components/layout/file-layout";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { useFileStore } from "@/store/file-store";
import { Send } from 'lucide-react';
import React, { useEffect, useState, use } from "react";
import { useChat } from 'ai/react';
import { API_BASE_URL } from "@/config";
import { fetchClient } from "@/lib/api/fetch-client";
import { useToast } from "@/hooks/use-toast";

type Params = Promise<{ fileId: string }>
type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>

interface ChatPageProps {
  params: Params;
  searchParams?: SearchParams;
}

interface StatusMessage {
  id: string;
  text: string;
  category: 'podcast' | 'flashcard' | 'quiz';
}

interface GenerateOptions {
  podcast: boolean;
  quiz: boolean;
  flashcard: boolean;
}

export default function ChatPage({ params, searchParams }: ChatPageProps) {
  const resolvedParams = use(params);
  const fileId = resolvedParams.fileId;
  const { toast } = useToast();
  const { selectedFile } = useFileStore();
  
  // Local state
  const [statusMessages, setStatusMessages] = useState<StatusMessage[]>([]);
  const [generateOptions, setGenerateOptions] = useState<GenerateOptions>({
    podcast: false,
    quiz: false,
    flashcard: false
  });
  const [isGenerating, setIsGenerating] = useState(false);

  // Chat configuration
  const { messages, input, handleInputChange, handleSubmit: handleChatSubmit, isLoading } = useChat({
    api: `${API_BASE_URL}/api/chat`,
    body: {
      file_id:fileId
    }
  });

  // Handle checkbox changes
  const handleCheckboxChange = (option: keyof GenerateOptions) => {
    setGenerateOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  // Generate learning materials
  const handleGenerate = async (userInput: string) => {
    try {
      setIsGenerating(true);
      const response = await fetchClient(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        body: JSON.stringify({
          query: userInput,
          file_id: fileId,
          podcast: generateOptions.podcast,
          quiz: generateOptions.quiz,
          flashcards: generateOptions.flashcard
        })
      });

      if (!response.ok) {
        throw new Error('Generation failed');
      }

      const data = await response.json();

      // Add status messages for each type of content being generated
      const newStatusMessages: StatusMessage[] = [];

      if (data.is_podcast_generating) {
        newStatusMessages.push({
          id: 'podcast-status-' + Date.now(),
          text: 'Podcast generation in progress. You will be notified when it\'s ready.',
          category: 'podcast'
        });
      }

      if (data.is_quiz_generating) {
        newStatusMessages.push({
          id: 'quiz-status-' + Date.now(),
          text: 'Quiz generation in progress. You will be notified when it\'s ready.',
          category: 'quiz'
        });
      }

      if (data.is_flashcards_generating) {
        newStatusMessages.push({
          id: 'flashcard-status-' + Date.now(),
          text: 'Flashcard generation in progress. You will be notified when it\'s ready.',
          category: 'flashcard'
        });
      }

      setStatusMessages(prev => [...prev, ...newStatusMessages]);
      
      toast({
        title: "Generation Started",
        description: "Your learning materials are being generated.",
        variant: "default"
      });

    } catch (error) {
      console.error('Generation error:', error);
      toast({
        title: "Generation Failed",
        description: "Failed to generate learning materials. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Check if any generation options are selected
    const hasGenerationOptions = Object.values(generateOptions).some(Boolean);

    if (hasGenerationOptions) {
      // If generation options are selected, call generate endpoint
      await handleGenerate(input);
    } else {
      // Otherwise, proceed with normal chat
      handleChatSubmit(e);
    }
  };

  return (
    <FileLayout fileId={fileId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Chat with Document
          </h1>
          <p className="text-muted-foreground">
            Ask questions about {selectedFile?.filename}
          </p>
        </div>

        <Card className="w-full min-h-[calc(100vh-12rem)] flex flex-col">
          {/* Chat Messages Area */}
          <div className="flex-1 p-4 space-y-4 overflow-y-auto">
            {messages.length === 0 && statusMessages.length === 0 ? (
              <div className="text-center text-muted-foreground">
                Start chatting with your document
              </div>
            ) : (
              <>
                {/* Chat Messages */}
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground ml-auto max-w-[80%]'
                        : 'bg-muted mr-auto max-w-[80%]'
                    }`}
                  >
                    {message.content}
                  </div>
                ))}
                
                {/* Status Messages */}
                {statusMessages.map((message) => (
                  <div
                    key={message.id}
                    className="p-4 rounded-lg bg-accent/20 mx-auto max-w-[90%] text-center"
                  >
                    <div className="text-sm font-semibold mb-1">
                      {message.category.charAt(0).toUpperCase() + message.category.slice(1)}
                    </div>
                    {message.text}
                  </div>
                ))}
              </>
            )}
            {(isLoading || isGenerating) && (
              <div className="flex justify-center items-center h-8">
                <div className="animate-pulse bg-gray-300 h-4 w-4 rounded-full"></div>
                <div className="animate-pulse bg-gray-300 h-4 w-4 rounded-full mx-1"></div>
                <div className="animate-pulse bg-gray-300 h-4 w-4 rounded-full"></div>
              </div>
            )}
          </div>

          {/* Generation Options */}
          <div className="border-t p-4">
            <div className="flex gap-6 mb-4">
              <label className="flex items-center gap-2">
                <Checkbox
                  checked={generateOptions.podcast}
                  onCheckedChange={() => handleCheckboxChange('podcast')}
                  disabled={isLoading || isGenerating}
                />
                <span>Generate Podcast</span>
              </label>
              <label className="flex items-center gap-2">
                <Checkbox
                  checked={generateOptions.quiz}
                  onCheckedChange={() => handleCheckboxChange('quiz')}
                  disabled={isLoading || isGenerating}
                />
                <span>Generate Quiz</span>
              </label>
              <label className="flex items-center gap-2">
                <Checkbox
                  checked={generateOptions.flashcard}
                  onCheckedChange={() => handleCheckboxChange('flashcard')}
                  disabled={isLoading || isGenerating}
                />
                <span>Generate Flashcards</span>
              </label>
            </div>

            {/* Input Area */}
            <form className="flex gap-2" onSubmit={handleSubmit}>
              <Input
                placeholder="Ask a question..."
                className="flex-1"
                value={input}
                onChange={handleInputChange}
                disabled={isLoading || isGenerating}
              />
              <Button 
                type="submit" 
                disabled={isLoading || isGenerating}
                className="min-w-[40px]"
              >
                {isLoading || isGenerating ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-current"></div>
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </FileLayout>
  );
}