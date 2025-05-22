"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/lib/auth";
import { createApiClient, ScrapeResult } from "@/lib/api";
import { ScrapeForm } from "./scrape-form";
import { JobList } from "./job-list";
import { ResultsView } from "./results-view";

export function Scraper() {
  const { apiKey } = useAuth();
  const [activeTab, setActiveTab] = useState("new");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [results, setResults] = useState<ScrapeResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Initialize API client
  const apiClient = apiKey ? createApiClient(apiKey) : null;
  
  // Handle starting a scrape job
  const handleStartScraping = (jobId: string, status: string) => {
    setJobId(jobId);
    setJobStatus(status);
    
    // Start polling for job status
    if (apiClient) {
      pollJobStatus(jobId);
    }
  };
  
  // Poll for job status
  const pollJobStatus = async (id: string) => {
    if (!apiClient) return;
    
    try {
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        const resultsData = await apiClient.getJobResults(id);
        setResults(resultsData.results);
      } else if (job.status === "failed") {
        setError(`Job failed: ${job.error_message}`);
      } else {
        // Continue polling (every 2 seconds)
        setTimeout(() => pollJobStatus(id), 2000);
      }
    } catch (err) {
      setError(`Failed to get job status: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Handle viewing job results
  const handleViewResults = async (id: string) => {
    if (!apiClient) return;
    
    try {
      setJobId(id);
      
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        const resultsData = await apiClient.getJobResults(id);
        setResults(resultsData.results);
        // Switch to results view
        setActiveTab("results");
      } else {
        setError(`Job is ${job.status}, cannot view results yet`);
      }
    } catch (err) {
      setError(`Failed to load job results: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  return (
    <div className="container mx-auto py-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="new">New Scrape</TabsTrigger>
          <TabsTrigger value="jobs">My Jobs</TabsTrigger>
          <TabsTrigger value="results" disabled={!results}>Results</TabsTrigger>
        </TabsList>
        
        <TabsContent value="new">
          <ScrapeForm
            onStartScraping={handleStartScraping}
            setError={setError}
          />
        </TabsContent>
        
        <TabsContent value="jobs">
          <JobList
            onViewResults={handleViewResults}
            setError={setError}
          />
        </TabsContent>
        
        <TabsContent value="results">
          {results && jobId && jobStatus && (
            <ResultsView
              results={results}
              jobId={jobId}
              status={jobStatus}
            />
          )}
        </TabsContent>
      </Tabs>
      
      {error && (
        <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200 rounded-md">
          {error}
        </div>
      )}
    </div>
  );
} 