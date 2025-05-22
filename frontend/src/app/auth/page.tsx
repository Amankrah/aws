'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { LoginForm } from '@/components/auth/login-form';
import { RegisterForm } from '@/components/auth/register-form';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Redirect to home if already authenticated
  if (isAuthenticated && !isLoading) {
    router.push('/');
    return null;
  }

  return (
    <div className="container max-w-5xl mx-auto py-12 px-4">
      <div className="max-w-md mx-auto">
        <Card className="p-1">
          <div className="grid grid-cols-2 gap-1 mb-6">
            <Button
              variant={activeTab === 'login' ? 'default' : 'ghost'}
              className="rounded-sm"
              onClick={() => setActiveTab('login')}
            >
              Login
            </Button>
            <Button
              variant={activeTab === 'register' ? 'default' : 'ghost'}
              className="rounded-sm"
              onClick={() => setActiveTab('register')}
            >
              Register
            </Button>
          </div>
          
          <div className="p-4">
            {activeTab === 'login' ? <LoginForm /> : <RegisterForm />}
          </div>
        </Card>
      </div>
    </div>
  );
} 