"use client";

import { useState } from "react";
import { Button } from "./button";
import { Input } from "./input";
import { 
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "./card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "./tabs";
import { Loader2 } from "lucide-react";
import { createApiClient, ScrapeOptions, ScrapeJob, ScrapeResult } from "../../lib/api";

// Check if we have an API key in localStorage
const getStoredApiKey = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("scraper_api_key") || "";
  }
  return "";
};

const Scraper = () => {
  const [apiKey, setApiKey] = useState(getStoredApiKey());
  const [apiBaseUrl, setApiBaseUrl] = useState("http://localhost:8001");
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [advancedOptions, setAdvancedOptions] = useState<ScrapeOptions>({
    formats: ["markdown", "html"],
    max_depth: 2,
    allow_external_links: false,
    only_main_content: true,
    parse_pdf: true,
  });
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [results, setResults] = useState<ScrapeResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  
  // Initialize API client
  const apiClient = createApiClient(apiKey, apiBaseUrl);
  
  // Save API key to localStorage when it changes
  const handleApiKeyChange = (newKey: string) => {
    setApiKey(newKey);
    if (typeof window !== "undefined") {
      localStorage.setItem("scraper_api_key", newKey);
    }
  };
  
  // Handle form submission
  const handleSubmit = async () => {
    if (!apiKey) {
      setError("API key is required");
      return;
    }
    
    if (!query) {
      setError("Query is required");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.startScraping(query, domain || undefined, advancedOptions);
      setJobId(response.job_id);
      setJobStatus(response.status);
      
      // Start polling for job status
      pollJobStatus(response.job_id);
    } catch (err) {
      setError(`Failed to start scraping: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Poll for job status
  const pollJobStatus = async (id: string) => {
    try {
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        const results = await apiClient.getJobResults(id);
        setResults(results.results);
      } else if (job.status === "failed") {
        setError(`Job failed: ${job.error_message}`);
      } else {
        // Continue polling
        setTimeout(() => pollJobStatus(id), 2000);
      }
    } catch (err) {
      setError(`Failed to get job status: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Fetch existing jobs
  const fetchJobs = async () => {
    if (!apiKey) return;
    
    try {
      setLoading(true);
      const jobs = await apiClient.listJobs();
      setJobs(jobs);
    } catch (err) {
      setError(`Failed to fetch jobs: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Load job results
  const loadJobResults = async (id: string) => {
    try {
      setLoading(true);
      setJobId(id);
      
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        const results = await apiClient.getJobResults(id);
        setResults(results.results);
      } else {
        setError(`Job is ${job.status}, cannot load results yet`);
      }
    } catch (err) {
      setError(`Failed to load job results: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto py-6">
      <Tabs defaultValue="scrape">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="scrape">New Scrape</TabsTrigger>
          <TabsTrigger value="jobs" onClick={fetchJobs}>My Jobs</TabsTrigger>
        </TabsList>
        
        {/* Scrape Tab */}
        <TabsContent value="scrape">
          <Card>
            <CardHeader>
              <CardTitle>Scraper</CardTitle>
              <CardDescription>
                Extract information from the web by entering a search query or specific domain
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <label htmlFor="query" className="text-sm font-medium">Search Query</label>
                  <Input
                    id="query"
                    placeholder="What would you like to search for?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
                
                <div className="grid gap-2">
                  <label htmlFor="domain" className="text-sm font-medium">Domain (Optional)</label>
                  <Input
                    id="domain"
                    placeholder="e.g., example.com"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                  />
                  <p className="text-sm text-muted-foreground">
                    Provide a specific domain to focus the search
                  </p>
                </div>
                
                <div className="grid gap-2">
                  <div className="text-sm font-medium">Advanced Options</div>
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="parse-pdf" 
                      checked={advancedOptions.parse_pdf}
                      onChange={(e) => 
                        setAdvancedOptions({...advancedOptions, parse_pdf: e.target.checked})
                      }
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="parse-pdf" className="text-sm">Parse PDF files</label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="only-main-content" 
                      checked={advancedOptions.only_main_content}
                      onChange={(e) => 
                        setAdvancedOptions({...advancedOptions, only_main_content: e.target.checked})
                      }
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="only-main-content" className="text-sm">Only extract main content</label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="allow-external-links" 
                      checked={advancedOptions.allow_external_links}
                      onChange={(e) => 
                        setAdvancedOptions({...advancedOptions, allow_external_links: e.target.checked})
                      }
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="allow-external-links" className="text-sm">Follow external links</label>
                  </div>
                  
                  <div className="grid gap-2 mt-2">
                    <label htmlFor="max-depth" className="text-sm font-medium">Maximum Crawl Depth</label>
                    <Input
                      id="max-depth"
                      type="number"
                      min="1"
                      max="10"
                      value={advancedOptions.max_depth}
                      onChange={(e) => 
                        setAdvancedOptions({...advancedOptions, max_depth: parseInt(e.target.value) || 2})
                      }
                    />
                  </div>
                  
                  <div className="grid gap-2 mt-2">
                    <label htmlFor="api-key" className="text-sm font-medium">API Key</label>
                    <Input
                      id="api-key"
                      type="password"
                      placeholder="Your API Key"
                      value={apiKey}
                      onChange={(e) => handleApiKeyChange(e.target.value)}
                    />
                  </div>
                  
                  <div className="grid gap-2 mt-2">
                    <label htmlFor="api-url" className="text-sm font-medium">API Base URL</label>
                    <Input
                      id="api-url"
                      placeholder="http://localhost:8001"
                      value={apiBaseUrl}
                      onChange={(e) => setApiBaseUrl(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button 
                className="w-full" 
                onClick={handleSubmit}
                disabled={loading || !apiKey}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  "Start Scraping"
                )}
              </Button>
            </CardFooter>
          </Card>
          
          {/* Results Display */}
          {results && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Scraping Results</CardTitle>
                <CardDescription>
                  Job ID: {jobId} | Status: {jobStatus}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.map((result, idx) => (
                    <div key={idx} className="border p-4 rounded-md">
                      <h3 className="font-semibold text-lg">{result.title}</h3>
                      {result.url && (
                        <a 
                          href={result.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:underline text-sm"
                        >
                          {result.url}
                        </a>
                      )}
                      <div className="mt-2">
                        {result.content_type === 'markdown' ? (
                          <div className="prose max-w-none dark:prose-invert">
                            <pre className="whitespace-pre-wrap">{result.content}</pre>
                          </div>
                        ) : result.content_type === 'json' ? (
                          <pre className="bg-gray-50 dark:bg-gray-900 p-2 rounded-md overflow-auto">
                            {JSON.stringify(JSON.parse(result.content), null, 2)}
                          </pre>
                        ) : (
                          <div>{result.content}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          
          {error && (
            <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200 rounded-md">
              {error}
            </div>
          )}
        </TabsContent>
        
        {/* Jobs Tab */}
        <TabsContent value="jobs">
          <Card>
            <CardHeader>
              <CardTitle>My Scraping Jobs</CardTitle>
              <CardDescription>
                View and manage your previous scraping jobs
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center p-4">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : jobs.length > 0 ? (
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <div key={job.job_id} className="border p-4 rounded-md">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold">{job.query}</h3>
                          <p className="text-sm text-muted-foreground">
                            Created: {new Date(job.created_at).toLocaleString()}
                          </p>
                          <div className="flex items-center mt-1">
                            <span 
                              className={`inline-block w-2 h-2 rounded-full mr-2 ${
                                job.status === 'completed' ? 'bg-green-500' : 
                                job.status === 'failed' ? 'bg-red-500' : 
                                'bg-yellow-500'
                              }`}
                            />
                            <span className="text-sm">{job.status}</span>
                          </div>
                        </div>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => loadJobResults(job.job_id)}
                          disabled={job.status !== 'completed'}
                        >
                          View Results
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  No jobs found. Start a new scraping job to see results here.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Scraper; 