// components/file/pdf-viewer.tsx
'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  AreaHighlight,
  Popup,
  Tip
} from 'react-pdf-highlighter';
import type { IHighlight, NewHighlight, ScaledPosition, Content } from 'react-pdf-highlighter';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';
import { FileResponse } from '@/types/file';
import { Skeleton } from '@/components/ui/skeleton';
import "react-pdf-highlighter/dist/style.css";

interface PDFViewerProps {
  file: FileResponse;
}

interface HighlightPopupProps {
  comment: {
    text: string;
    emoji?: string;
  };
}

const getNextId = () => String(Math.random()).slice(2);

const HighlightPopup = ({ comment }: HighlightPopupProps) => (
  comment.text ? (
    <div className="bg-white p-2 rounded shadow-lg">
      {comment.emoji} {comment.text}
    </div>
  ) : null
);

export function PDFViewer({ file }: PDFViewerProps) {
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlights, setHighlights] = useState<Array<IHighlight>>([]);
  
  const scrollViewerTo = useRef<(highlight: IHighlight) => void>(() => {});
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  const LoadingFallback = useCallback(() => (
    <div className="space-y-4 p-4">
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-96 w-full" />
    </div>
  ), []);

  const addHighlight = (highlight: NewHighlight) => {
    console.log("Saving highlight", highlight);
    setHighlights(prevHighlights => [
      { ...highlight, id: getNextId() },
      ...prevHighlights
    ]);
  };

  const updateHighlight = (
    highlightId: string,
    position: Partial<ScaledPosition>,
    content: Partial<Content>
  ) => {
    console.log("Updating highlight", highlightId, position, content);
    setHighlights(prevHighlights =>
      prevHighlights.map(h => {
        const {
          id,
          position: originalPosition,
          content: originalContent,
          ...rest
        } = h;
        return id === highlightId
          ? {
              id,
              position: { ...originalPosition, ...position },
              content: { ...originalContent, ...content },
              ...rest
            }
          : h;
      })
    );
  };

  if (!mounted) {
    return <LoadingFallback />;
  }

  if (!file || !file.download_url) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        No file selected
      </div>
    );
  }

  return (
    <Card className="w-full h-[calc(100vh-12rem)] relative overflow-hidden">
      <Button
        variant="outline"
        size="sm"
        className="absolute top-4 right-4 z-10"
        onClick={() => window.open(file.download_url, '_blank')}
      >
        <Download className="h-4 w-4 mr-2" />
        Download
      </Button>

      <div className="absolute inset-0 pt-16">
        {error ? (
          <div className="flex items-center justify-center h-full text-destructive">
            {error}
          </div>
        ) : (
          <PdfLoader
            url={file.download_url}
            beforeLoad={<LoadingFallback />}
            onError={() => setError('Failed to load PDF file')}
          >
            {(pdfDocument) => (
              <div className="h-full">
                <PdfHighlighter
                  pdfDocument={pdfDocument}
                  enableAreaSelection={(event) => event.altKey}
                  onScrollChange={() => {}}
                  scrollRef={(scrollTo) => {
                    scrollViewerTo.current = scrollTo;
                  }}
                  onSelectionFinished={(
                    position,
                    content,
                    hideTipAndSelection,
                    transformSelection
                  ) => (
                    <Tip
                      onOpen={transformSelection}
                      onConfirm={(comment) => {
                        addHighlight({ content, position, comment });
                        hideTipAndSelection();
                      }}
                    />
                  )}
                  highlightTransform={(
                    highlight,
                    index,
                    setTip,
                    hideTip,
                    viewportToScaled,
                    screenshot,
                    isScrolledTo
                  ) => {
                    const isTextHighlight = !highlight.content?.image;

                    const component = isTextHighlight ? (
                      <Highlight
                        isScrolledTo={isScrolledTo}
                        position={highlight.position}
                        comment={highlight.comment}
                      />
                    ) : (
                      <AreaHighlight
                        isScrolledTo={isScrolledTo}
                        highlight={highlight}
                        onChange={(boundingRect) => {
                          updateHighlight(
                            highlight.id,
                            { boundingRect: viewportToScaled(boundingRect) },
                            { image: screenshot(boundingRect) }
                          );
                        }}
                      />
                    );

                    return (
                      <Popup
                        popupContent={<HighlightPopup {...highlight} />}
                        onMouseOver={(popupContent) =>
                          setTip(highlight, () => popupContent)
                        }
                        onMouseOut={hideTip}
                        key={index}
                      >
                        {component}
                      </Popup>
                    );
                  }}
                  highlights={highlights}
                />
              </div>
            )}
          </PdfLoader>
        )}
      </div>
    </Card>
  );
}