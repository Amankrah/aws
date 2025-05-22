'use client';

import { useState, useRef } from 'react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

export function RegisterForm() {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const apiKeyRef = useRef<HTMLElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const newApiKey = await register(
        formData.username,
        formData.email,
        formData.password
      );
      setApiKey(newApiKey);
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (apiKey) {
      try {
        await navigator.clipboard.writeText(apiKey);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    }
  };

  const downloadApiKey = () => {
    if (apiKey) {
      const element = document.createElement('a');
      const file = new Blob([
        `API Key for ${formData.username}\n`,
        `Generated on: ${new Date().toLocaleString()}\n\n`,
        apiKey
      ], { type: 'text/plain' });
      
      element.href = URL.createObjectURL(file);
      element.download = `api-key-${formData.username}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  if (apiKey) {
    return (
      <Card className="w-full max-w-md p-6 shadow-md">
        <div className="space-y-6 text-center">
          <h1 className="text-3xl font-bold text-green-600 dark:text-green-500">
            Registration Successful!
          </h1>
          <p className="text-gray-700 dark:text-gray-300">
            Your account has been created and you are now logged in.
          </p>
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-md">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Your API Key (save this somewhere safe):
              </p>
              
              <div className="flex space-x-2">
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={copyToClipboard}
                  className="text-xs"
                >
                  {copySuccess ? 'Copied!' : 'Copy'}
                </Button>
                
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={downloadApiKey}
                  className="text-xs"
                >
                  Download
                </Button>
              </div>
            </div>
            
            <code 
              ref={apiKeyRef}
              className="block p-3 bg-white dark:bg-gray-900 rounded border text-sm overflow-x-auto break-all"
            >
              {apiKey}
            </code>
          </div>
          <p className="text-sm text-gray-500">
            You will need this API key to log in to your account in the future.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md p-6 shadow-md">
      <div className="space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Register</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Create an account to access the web scraper
          </p>
        </div>

        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="username" className="text-sm font-medium">
              Username
            </label>
            <Input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username"
              required
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password"
              required
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="text-sm font-medium">
              Confirm Password
            </label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
              className="w-full"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Register'}
          </Button>
        </form>
      </div>
    </Card>
  );
} 