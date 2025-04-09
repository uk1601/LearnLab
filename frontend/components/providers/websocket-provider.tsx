'use client';

import React, { createContext, useContext, useEffect, useRef } from 'react';
import { useAuth } from './auth-provider';
import { useToast } from '@/hooks/use-toast';

interface WebSocketContextType {
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false
});

// Create a singleton WebSocket instance
let globalWs: WebSocket | null = null;
let reconnectTimeout: NodeJS.Timeout | null = null;

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isConnected, setIsConnected] = React.useState(false);
  const isInitialMount = useRef(true);

  const connect = React.useCallback(() => {
    if (!user || globalWs?.readyState === WebSocket.OPEN) {
      return;
    }

    // Get token from cookie
    const token = document.cookie
      .split('; ')
      .find(row => row.startsWith('access_token='))
      ?.split('=')[1];

    if (!token) {
      console.error('No access token found');
      return;
    }

    // const wsUrl = `http://backend:8000/ws?token=${token}`;
    // Get the base URL from environment variables
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://backend:8000" || "http://localhost:8000" ;

    // Replace http:// with ws:// for WebSocket protocol
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsBase = baseUrl.replace(/^http(s)?:\/\//, '');
    const wsUrl = `${wsProtocol}://${wsBase}/ws?token=${token}`;
    console.log(process.env.NEXT_PUBLIC_WS_URL)

    console.log('Connecting to WebSocket...');
    
    globalWs = new WebSocket(wsUrl);

    globalWs.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      // Only show toast on initial connection or reconnection after error
      if (isInitialMount.current) {
        toast({
          title: "Connected",
          description: "Real-time notifications enabled",
          variant: "default",
          duration: 3000
        });
        isInitialMount.current = false;
      }
    };

    globalWs.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          toast({
            title: data.title,
            description: data.message,
            variant: data["variant"]|| "default",
            duration: data.duration || 5000
          });
        }
      } catch (error) {
        console.error('Error processing websocket message:', error);
      }
    };

    globalWs.onclose = (event) => {
      console.log('WebSocket Closed:', event.code, event.reason);
      setIsConnected(false);
      globalWs = null;

      if (!event.wasClean) {
        toast({
          title: "Connection Lost",
          description: "Attempting to reconnect...",
          variant: "destructive",
          duration: 3000
        });
      }

      // Attempt to reconnect after 3 seconds
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      reconnectTimeout = setTimeout(() => {
        if (user) {
          console.log('Attempting to reconnect...');
          connect();
        }
      }, 3000);
    };

    globalWs.onerror = (error) => {
      console.error('WebSocket Error:', error);
      if (isInitialMount.current) {
        toast({
          title: "Connection Error",
          description: "Failed to establish connection",
          variant: "destructive",
          duration: 3000
        });
      }
    };

    // Keep connection alive with ping every 30 seconds
    const pingInterval = setInterval(() => {
      if (globalWs?.readyState === WebSocket.OPEN) {
        globalWs.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    // Cleanup interval on unmount of the app (not on page transitions)
    return () => {
      clearInterval(pingInterval);
    };
  }, [user, toast]);

  useEffect(() => {
    // Only connect if we don't have an existing connection
    if (user && !globalWs) {
      connect();
    }

    // Only clean up on app unmount
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [user, connect]);

  return (
    <WebSocketContext.Provider value={{ isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export const useWebSocket = () => useContext(WebSocketContext);