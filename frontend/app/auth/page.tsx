'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoginForm } from '@/components/auth/login-form';
import { RegisterForm } from '@/components/auth/register-form';
import { Suspense } from 'react';
import { Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

function AuthContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get('tab') || 'login';

  const handleTabChange = (value: string) => {
    router.push(`/auth?tab=${value}`);
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-y-0 right-0 w-1/2 bg-accent/5" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-border" />
      </div>

      <div className="container-base min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Logo & Header */}
            <div className="text-center space-y-2">
              <div className="inline-flex items-center justify-center gap-2 mb-4">
                <Sparkles className="h-6 w-6 text-accent" />
                <span className="text-2xl font-bold">LearnLab</span>
              </div>
              <h1 className="text-2xl font-semibold tracking-tight">
                {tab === 'login' ? 'Welcome back' : 'Create your account'}
              </h1>
              <p className="text-sm text-muted-foreground">
                {tab === 'login' 
                  ? 'Sign in to continue to your dashboard' 
                  : 'Start your learning journey today'}
              </p>
            </div>

            {/* Auth Card */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card-base border-2"
            >
              <Tabs value={tab} onValueChange={handleTabChange} className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger value="login">
                    Sign In
                  </TabsTrigger>
                  <TabsTrigger value="register">
                    Sign Up
                  </TabsTrigger>
                </TabsList>
                
                <div className="p-6 pt-2">
                  <TabsContent value="login" className="mt-0">
                    <LoginForm />
                  </TabsContent>
                  
                  <TabsContent value="register" className="mt-0">
                    <RegisterForm />
                  </TabsContent>
                </div>
              </Tabs>
            </motion.div>

            {/* Additional Links */}
            <div className="text-center text-sm">
              <button 
                onClick={() => router.push('/')}
                className="text-muted-foreground hover:text-accent transition-colors"
              >
                ← Back to home
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AuthContent />
    </Suspense>
  );
}