'use client';

import { useState, useRef } from 'react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function UserProfile() {
  const { user, logout, refreshApiKey, updateFirecrawlKey, updateAnthropicKey } = useAuth();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isUpdatingFirecrawl, setIsUpdatingFirecrawl] = useState(false);
  const [isUpdatingAnthropic, setIsUpdatingAnthropic] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [firecrawlKey, setFirecrawlKey] = useState(user?.firecrawl_key || '');
  const [anthropicKey, setAnthropicKey] = useState(user?.anthropic_key || '');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const apiKeyRef = useRef<HTMLElement>(null);

  if (!user) {
    return null;
  }

  const handleRefreshApiKey = async () => {
    setError(null);
    setSuccessMessage(null);
    setIsRefreshing(true);
    
    try {
      const apiKey = await refreshApiKey();
      setNewApiKey(apiKey);
    } catch {
      setError('Failed to refresh API key. Please try again.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const copyToClipboard = async () => {
    if (newApiKey) {
      try {
        await navigator.clipboard.writeText(newApiKey);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    }
  };

  const downloadApiKey = () => {
    if (newApiKey) {
      const element = document.createElement('a');
      const file = new Blob([
        `API Key for ${user.username}\n`,
        `Generated on: ${new Date().toLocaleString()}\n\n`,
        newApiKey
      ], { type: 'text/plain' });
      
      element.href = URL.createObjectURL(file);
      element.download = `api-key-${user.username}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  const handleUpdateFirecrawlKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsUpdatingFirecrawl(true);
    
    try {
      await updateFirecrawlKey(firecrawlKey);
      setSuccessMessage('Firecrawl API key updated successfully');
    } catch {
      setError('Failed to update Firecrawl API key. Please try again.');
    } finally {
      setIsUpdatingFirecrawl(false);
    }
  };

  const handleUpdateAnthropicKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsUpdatingAnthropic(true);
    
    try {
      await updateAnthropicKey(anthropicKey);
      setSuccessMessage('Anthropic API key updated successfully');
    } catch {
      setError('Failed to update Anthropic API key. Please try again.');
    } finally {
      setIsUpdatingAnthropic(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl p-6 shadow-md">
      <div className="space-y-6">
        <div className="space-y-2">
          <h2 className="text-2xl font-bold">User Profile</h2>
          <p className="text-gray-500 dark:text-gray-400">
            Your account information and API settings
          </p>
        </div>

        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 rounded-md">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="p-3 text-sm text-green-500 bg-green-50 dark:bg-green-900/20 rounded-md">
            {successMessage}
          </div>
        )}

        {newApiKey && (
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-md space-y-3">
            <p className="text-sm font-medium text-green-600 dark:text-green-400">
              Your API key has been refreshed
            </p>
            <div className="p-3 bg-white dark:bg-gray-800 rounded border">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  New API Key:
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
                className="block text-sm overflow-x-auto break-all"
              >
                {newApiKey}
              </code>
            </div>
            <p className="text-xs text-gray-500">
              Store this key safely. It will not be shown again.
            </p>
          </div>
        )}

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Username</p>
              <p className="font-medium">{user.username}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Email</p>
              <p className="font-medium">{user.email}</p>
            </div>
          </div>
          
          <div className="pt-4 border-t">
            <p className="text-sm font-medium text-gray-500 mb-1">Usage Quota</p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-1">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${(user.usage_count / user.usage_quota) * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500">
              {user.usage_count} of {user.usage_quota} requests used
            </p>
          </div>
        </div>

        <div className="pt-4 border-t">
          <Tabs defaultValue="app">
            <TabsList className="mb-4">
              <TabsTrigger value="app">App API Keys</TabsTrigger>
              <TabsTrigger value="services">Service API Keys</TabsTrigger>
            </TabsList>
            
            <TabsContent value="app" className="space-y-4">
              <div>
                <h3 className="text-lg font-medium mb-2">App Authentication</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Your main API key for authenticating with this application
                </p>
                
                <Button
                  onClick={handleRefreshApiKey}
                  disabled={isRefreshing}
                  variant="outline"
                  className="w-full"
                >
                  {isRefreshing ? 'Refreshing...' : 'Refresh API Key'}
                </Button>
              </div>
            </TabsContent>
            
            <TabsContent value="services" className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-2">Firecrawl API Key</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Used for web crawling and data extraction services
                </p>
                
                <form onSubmit={handleUpdateFirecrawlKey} className="space-y-3">
                  <Input
                    value={firecrawlKey}
                    onChange={(e) => setFirecrawlKey(e.target.value)}
                    placeholder="Enter your Firecrawl API key"
                    type="password"
                  />
                  <Button 
                    type="submit" 
                    variant="outline"
                    disabled={isUpdatingFirecrawl}
                    className="w-full"
                  >
                    {isUpdatingFirecrawl ? 'Updating...' : 'Update Firecrawl Key'}
                  </Button>
                </form>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Anthropic API Key</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Used for AI text generation and analysis with Claude models
                </p>
                
                <form onSubmit={handleUpdateAnthropicKey} className="space-y-3">
                  <Input
                    value={anthropicKey}
                    onChange={(e) => setAnthropicKey(e.target.value)}
                    placeholder="Enter your Anthropic API key"
                    type="password"
                  />
                  <Button 
                    type="submit" 
                    variant="outline"
                    disabled={isUpdatingAnthropic}
                    className="w-full"
                  >
                    {isUpdatingAnthropic ? 'Updating...' : 'Update Anthropic Key'}
                  </Button>
                </form>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="pt-4 border-t">
          <Button 
            onClick={logout} 
            variant="destructive"
            className="w-full"
          >
            Logout
          </Button>
        </div>
      </div>
    </Card>
  );
} 