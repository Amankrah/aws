"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrapeResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Download, ExternalLink, FileText, Info, Database, Copy } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ResultsViewProps {
  results: ScrapeResult[];
  jobId: string;
  status: string;
}

export function ResultsView({ results, jobId }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<string>(results[0]?.url || "result-0");
  const [copiedText, setCopiedText] = useState<string | null>(null);
  
  // Download results as JSON
  const downloadResults = () => {
    const element = document.createElement('a');
    const file = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    element.href = URL.createObjectURL(file);
    element.download = `scrape-results-${jobId}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };
  
  // Copy content to clipboard
  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(id);
    setTimeout(() => setCopiedText(null), 2000);
  };
  
  // Get content display based on content type
  const renderContent = (result: ScrapeResult, idx: number) => {
    const contentId = `content-${idx}`;
    
    if (result.content_type === 'markdown') {
      return (
        <div className="relative prose prose-sm max-w-none dark:prose-invert">
          <div className="absolute top-2 right-2">
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={() => copyToClipboard(result.content, contentId)}
            >
              {copiedText === contentId ? 
                <span className="text-xs text-green-600">Copied!</span> : 
                <Copy className="h-4 w-4" />
              }
            </Button>
          </div>
          <pre className="whitespace-pre-wrap bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto text-sm">
            {result.content}
          </pre>
        </div>
      );
    } else if (result.content_type === 'json') {
      try {
        const jsonData = JSON.parse(result.content);
        return (
          <div className="relative">
            <div className="absolute top-2 right-2">
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0"
                onClick={() => copyToClipboard(result.content, contentId)}
              >
                {copiedText === contentId ? 
                  <span className="text-xs text-green-600">Copied!</span> : 
                  <Copy className="h-4 w-4" />
                }
              </Button>
            </div>
            <pre className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto text-sm font-mono">
              {JSON.stringify(jsonData, null, 2)}
            </pre>
          </div>
        );
      } catch {
        return (
          <div className="bg-red-50 text-red-800 p-3 rounded-md">
            Invalid JSON content
          </div>
        );
      }
    } else if (result.content_type === 'html') {
      return (
        <div className="relative">
          <div className="absolute top-2 right-2">
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={() => copyToClipboard(result.content, contentId)}
            >
              {copiedText === contentId ? 
                <span className="text-xs text-green-600">Copied!</span> : 
                <Copy className="h-4 w-4" />
              }
            </Button>
          </div>
          <div className="overflow-hidden">
            <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto max-h-[500px]">
              <pre className="text-sm">{result.content}</pre>
            </div>
          </div>
        </div>
      );
    } else {
      return (
        <div className="relative">
          <div className="absolute top-2 right-2">
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={() => copyToClipboard(result.content, contentId)}
            >
              {copiedText === contentId ? 
                <span className="text-xs text-green-600">Copied!</span> : 
                <Copy className="h-4 w-4" />
              }
            </Button>
          </div>
          <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto">
            {result.content}
          </div>
        </div>
      );
    }
  };
  
  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground">No results found for this job.</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-2xl">Scraping Results</CardTitle>
          <CardDescription>
            {results.length} result{results.length !== 1 ? 's' : ''} from job {jobId.substring(0, 8)}...
          </CardDescription>
        </div>
        <Button 
          size="sm" 
          onClick={downloadResults}
          className="flex items-center gap-1"
        >
          <Download className="h-4 w-4" />
          <span>Download JSON</span>
        </Button>
      </CardHeader>
      <CardContent>
        {results.length === 1 ? (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 pb-3 border-b">
              <h3 className="font-medium text-lg">{results[0].title || "Untitled"}</h3>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800">
                  {results[0].content_type}
                </span>
                {results[0].url && (
                  <a 
                    href={results[0].url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Open URL
                  </a>
                )}
              </div>
            </div>
            
            <div className="mt-4">
              {renderContent(results[0], 0)}
            </div>
            
            {results[0].metadata && Object.keys(results[0].metadata).length > 0 && (
              <div className="mt-6 border-t pt-4">
                <div className="flex items-center gap-1 text-sm font-medium mb-2">
                  <Info className="h-4 w-4" />
                  <span>Metadata</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto text-xs font-mono">
                  <pre>{JSON.stringify(results[0].metadata, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        ) : (
          <Tabs
            defaultValue={activeTab}
            value={activeTab}
            onValueChange={setActiveTab}
            className="mt-4"
          >
            <div className="mb-4 border-b pb-1">
              <TabsList className="h-auto bg-transparent p-0 overflow-x-auto flex-nowrap w-full flex justify-start space-x-2">
                {results.map((result, idx) => (
                  <TabsTrigger
                    key={`tab-${idx}`}
                    value={result.url || `result-${idx}`}
                    className="px-3 py-1.5 data-[state=active]:bg-primary/10 rounded"
                  >
                    <div className="flex items-center gap-1.5">
                      <FileText className="h-3.5 w-3.5" />
                      <span className="truncate max-w-[100px]">
                        {result.title ? (result.title.length > 25 ? result.title.substring(0, 25) + '...' : result.title) : `Result ${idx + 1}`}
                      </span>
                    </div>
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>
            
            {results.map((result, idx) => (
              <TabsContent 
                key={`content-${idx}`} 
                value={result.url || `result-${idx}`}
                className="m-0"
              >
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 pb-3 border-b">
                    <h3 className="font-medium text-lg">{result.title || `Result ${idx + 1}`}</h3>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center gap-1">
                        <Database className="h-3 w-3" />
                        {result.content_type}
                      </span>
                      {result.url && (
                        <a 
                          href={result.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
                        >
                          <ExternalLink className="h-3 w-3" />
                          Open URL
                        </a>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    {renderContent(result, idx)}
                  </div>
                  
                  {result.metadata && Object.keys(result.metadata).length > 0 && (
                    <div className="mt-6 border-t pt-4">
                      <div className="flex items-center gap-1 text-sm font-medium mb-2">
                        <Info className="h-4 w-4" />
                        <span>Metadata</span>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-900 p-3 rounded-md overflow-auto text-xs font-mono">
                        <pre>{JSON.stringify(result.metadata, null, 2)}</pre>
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
} 