'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchClient } from '@/lib/api/fetch-client';
import { API_ROUTES } from '@/config';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const setCookie = (name: string, value: string, days = 7) => {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
};

const removeCookie = (name: string) => {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];

      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await fetchClient(`${API_ROUTES.auth.me}`);

      if (!response.ok) {
        throw new Error('Failed to fetch user details');
      }

      const userData = await response.json();
      console.log('User data:', userData);
      setUser(userData);
    } catch (err) {
      console.error('Auth check failed:', err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      removeCookie('access_token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };
  const handleAuthSuccess = async (tokens: { access_token: string, refresh_token: string }) => {
    // Store tokens
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    setCookie('access_token', tokens.access_token);

    // Set dummy user data
    const response = await fetchClient(`${API_ROUTES.auth.me}`);

    if (!response.ok) {
      throw new Error('Failed to fetch user details');
    }

    const userData = await response.json();
    console.log('User data:', userData);
    setUser(userData);

    await router.push('/dashboard');
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      await handleAuthSuccess(data);
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      await login(userData.email, userData.password);
    } catch (err) {
      console.error('Registration error:', err);
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      const refreshToken = localStorage.getItem('refresh_token');
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];

      if (refreshToken && token) {
        await fetch(`${API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${decodeURIComponent(token)}`
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      }

      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      removeCookie('access_token');
      setUser(null);

      await router.push('/');
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}