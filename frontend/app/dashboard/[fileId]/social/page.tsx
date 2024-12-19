'use client';

import { use, useState } from 'react';
import { FileLayout } from "@/components/layout/file-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Twitter, FileText, Link as LinkIcon } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { fetchClient } from '@/lib/api/fetch-client';
import { API_BASE_URL } from '@/config';
// Types matching the backend schema
interface MarkdownContent {
  content: string;
  api_key: string;
  api_secret_key: string;
  access_token: string;
  access_token_secret: string;
}

interface BlogContent {
  title: string;
  body: string;
}

interface ContentRequest {
  query: string;
  pdf_title: string;
}

interface TwitterResponse {
  success: boolean;
  message: string;
  tweet_ids: string[] | null;
}

interface BloggerResponse {
  success: boolean;
  message: string;
  url: string | null;
}

interface ErrorResponse {
  detail: string;
}

interface ContentState {
  query: string;
  tweetContent: string;
  blogContent: string;
  blogTitle: string;
  blogUrl: string;
  isGenerating: boolean;
  isSharing: boolean;
  twitterCredentials: {
    api_key: string;
    api_secret_key: string;
    access_token: string;
    access_token_secret: string;
  };
}

type Params = Promise<{ fileId: string }>;

export default function SocialPage({ params }: { params: Params }) {
  const unwrappedParams = use(params);
  const [state, setState] = useState<ContentState>({
    query: '',
    tweetContent: '',
    blogContent: '',
    blogTitle: '',
    blogUrl: '',
    isGenerating: false,
    isSharing: false,
    twitterCredentials: {
      api_key: '',
      api_secret_key: '',
      access_token: '',
      access_token_secret: ''
    }
  });

  const handleGenerate = async (platform: 'tweet' | 'blog') => {
    try {
      setState(prev => ({ ...prev, isGenerating: true }));
      
      const response = await fetchClient(`${API_BASE_URL}/api/social/generate/${platform}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: state.query,
          pdf_title: unwrappedParams.fileId
        } as ContentRequest)
      });

      const data = await response.json();

      if (!response.ok) {
        const errorData = data as ErrorResponse;
        throw new Error(errorData.detail || 'Generation failed');
      }

      setState(prev => ({
        ...prev,
        tweetContent: platform === 'tweet' ? data.tweet : prev.tweetContent,
        blogContent: platform === 'blog' ? data.blog_content.body : prev.blogContent,
        blogTitle: platform === 'blog' ? data.blog_content.title : prev.blogTitle,
        blogUrl: platform === 'blog' && data.blog_content.url ? data.blog_content.url : prev.blogUrl
      }));

      toast({
        title: "Success",
        description: "Content generated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate content",
        variant: "destructive"
      });
    } finally {
      setState(prev => ({ ...prev, isGenerating: false }));
    }
  };

  const handleShare = async (platform: 'twitter' | 'blogger') => {
    try {
      setState(prev => ({ ...prev, isSharing: true }));
  
      const endpoint = platform === 'twitter' 
        ? `${API_BASE_URL}/api/social/twitter/thread`
        : `${API_BASE_URL}/api/social/blogger/post`;
  
      let requestBody: MarkdownContent | BlogContent;
  
      if (platform === 'twitter') {
        // Validate Twitter credentials
        const credentials = state.twitterCredentials;
        const missingFields = Object.entries(credentials)
          .filter(([_, value]) => !value.trim())
          .map(([key]) => key.replace(/_/g, ' '));
  
        if (missingFields.length > 0) {
          throw new Error(`Missing Twitter credentials: ${missingFields.join(', ')}`);
        }
  
        // Validate tweet content
        if (!state.tweetContent.trim()) {
          throw new Error('Tweet content cannot be empty');
        }
  
        // Format the request body for Twitter
        requestBody = {
          content: state.tweetContent.trim(),
          api_key: credentials.api_key.trim(),
          api_secret_key: credentials.api_secret_key.trim(),
          access_token: credentials.access_token.trim(),
          access_token_secret: credentials.access_token_secret.trim()
        };
  
        // Log the request for debugging (remove in production)
        console.log('Twitter request:', {
          ...requestBody,
          content: requestBody.content.substring(0, 50) + '...' // Truncate for logging
        });
      } else {
        requestBody = {
          title: state.blogTitle,
          body: state.blogContent
        };
      }
  
      const response = await fetchClient(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
  
      // Enhanced error handling
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || `Failed to share to ${platform} (Status: ${response.status})`;
        throw new Error(errorMessage);
      }
  
      const data = await response.json();
  
      // Handle Twitter-specific response
      if (platform === 'twitter') {
        const twitterData = data as TwitterResponse;
        if (!twitterData.success) {
          throw new Error(twitterData.message || 'Failed to post Twitter thread');
        }
        
        // Show success message with tweet IDs if available
        const successMessage = twitterData.tweet_ids?.length 
          ? `Thread posted successfully! ${twitterData.tweet_ids.length} tweets created.`
          : 'Thread posted successfully!';
          
        toast({
          title: "Success",
          description: successMessage
        });
        return;
      }
  
      // Handle Blogger response
      if (platform === 'blogger' && 'url' in data) {
        const bloggerData = data as BloggerResponse;
        if (bloggerData.url) {
          setState(prev => ({ ...prev, blogUrl: bloggerData.url! }));
        }
      }
  
      toast({
        title: "Success",
        description: `Content shared to ${platform} successfully`
      });
    } catch (error) {
      console.error('Sharing error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : `Failed to share to ${platform}`,
        variant: "destructive"
      });
    } finally {
      setState(prev => ({ ...prev, isSharing: false }));
    }
  };
  

  return (
    <FileLayout fileId={unwrappedParams.fileId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Share Learning</h1>
          <p className="text-muted-foreground">
            Create and share your learning insights
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Content Creator</CardTitle>
            <CardDescription>
              Generate and share content across platforms
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="twitter" className="space-y-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="twitter">Twitter Thread</TabsTrigger>
                <TabsTrigger value="blog">Blog Post</TabsTrigger>
              </TabsList>

              <TabsContent value="twitter" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Query</label>
                    <Textarea
                      placeholder="What would you like to share?"
                      value={state.query}
                      onChange={(e) => setState(prev => ({ ...prev, query: e.target.value }))}
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Generated Content</label>
                    <Textarea
                      value={state.tweetContent}
                      onChange={(e) => setState(prev => ({ ...prev, tweetContent: e.target.value }))}
                      placeholder="Generated content will appear here..."
                      className="min-h-[200px]"
                    />
                  </div>

                  {state.tweetContent && (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Twitter Credentials</label>
                      <div className="grid grid-cols-2 gap-4">
                        {Object.entries(state.twitterCredentials).map(([key, value]) => (
                          <Input
                            key={key}
                            placeholder={key.replace(/_/g, ' ')}
                            value={value}
                            onChange={(e) => setState(prev => ({
                              ...prev,
                              twitterCredentials: {
                                ...prev.twitterCredentials,
                                [key]: e.target.value
                              }
                            }))}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end gap-2">
                    <Button
                      onClick={() => handleGenerate('tweet')}
                      disabled={state.isGenerating || !state.query}
                    >
                      Generate
                    </Button>
                    <Button
                      onClick={() => handleShare('twitter')}
                      disabled={state.isSharing || !state.tweetContent}
                      className="gap-2"
                    >
                      <Twitter className="h-4 w-4" />
                      Share
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="blog" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Query</label>
                    <Textarea
                      placeholder="What would you like to write about?"
                      value={state.query}
                      onChange={(e) => setState(prev => ({ ...prev, query: e.target.value }))}
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Blog Title</label>
                    <Input
                      placeholder="Enter blog title..."
                      value={state.blogTitle}
                      onChange={(e) => setState(prev => ({ ...prev, blogTitle: e.target.value }))}
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Generated Content</label>
                    <Textarea
                      value={state.blogContent}
                      onChange={(e) => setState(prev => ({ ...prev, blogContent: e.target.value }))}
                      placeholder="Generated content will appear here..."
                      className="min-h-[200px]"
                    />
                  </div>

                  {state.blogUrl && (
                    <div className="flex items-center gap-2 p-4 bg-muted rounded-md">
                      <LinkIcon className="h-4 w-4" />
                      <a 
                        href={state.blogUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                      >
                        {state.blogUrl}
                      </a>
                    </div>
                  )}

                  <div className="flex justify-end gap-2">
                    <Button
                      onClick={() => handleGenerate('blog')}
                      disabled={state.isGenerating || !state.query}
                    >
                      Generate
                    </Button>
                    <Button
                      onClick={() => handleShare('blogger')}
                      disabled={state.isSharing || !state.blogContent || !state.blogTitle}
                      className="gap-2"
                    >
                      <FileText className="h-4 w-4" />
                      Share
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </FileLayout>
  );
}