"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { useAuth } from "@/lib/auth";
import { createApiClient, ScrapeResult } from "@/lib/api";
import { ScrapeForm } from "./scrape-form";
import { BatchForm } from "./batch-form";
import { SiteMap } from "./site-map";
import { MapResults } from "./map-results";
import { JobList } from "./job-list";
import { ResultsView } from "./results-view";
import { Card, CardContent } from "../ui/card";

const Scraper = () => {
  const { apiKey } = useAuth();
  const [activeTab, setActiveTab] = useState("scrape");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [results, setResults] = useState<ScrapeResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Site mapping state
  const [mapLinks, setMapLinks] = useState<string[]>([]);
  const [mapBaseUrl, setMapBaseUrl] = useState("");
  const [showMapResults, setShowMapResults] = useState(false);
  
  // Initialize API client
  const apiClient = apiKey ? createApiClient(apiKey) : null;
  
  useEffect(() => {
    // Clear error when tab changes
    setError(null);
    
    // Clear success message when tab changes
    if (successMessage) {
      setSuccessMessage(null);
    }
  }, [activeTab]);
  
  // Handle starting a scrape job
  const handleStartScraping = (jobId: string, status: string) => {
    setJobId(jobId);
    setJobStatus(status);
    setActiveTab("results");
    setResults(null); // Clear previous results
    setError(null);
    setSuccessMessage("Scraping job started successfully! Processing your request...");
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(null), 5000);
    
    // Start polling for job status
    if (apiClient) {
      setIsPolling(true);
      pollJobStatus(jobId);
    }
  };
  
  // Handle map completion
  const handleMapComplete = (links: string[], url: string) => {
    setMapLinks(links);
    setMapBaseUrl(url);
    setShowMapResults(true);
  };
  
  // Handle back from map results
  const handleMapBack = () => {
    setShowMapResults(false);
  };
  
  // Poll for job status
  const pollJobStatus = async (id: string) => {
    if (!apiClient) return;
    
    try {
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        setIsPolling(false);
        const resultsData = await apiClient.getJobResults(id);
        setResults(resultsData.results);
      } else if (job.status === "failed") {
        setIsPolling(false);
        setError(`Job failed: ${job.error_message}`);
      } else {
        // Continue polling (every 2 seconds)
        setTimeout(() => pollJobStatus(id), 2000);
      }
    } catch (err) {
      setIsPolling(false);
      setError(`Failed to get job status: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Handle viewing job results
  const handleViewResults = async (id: string) => {
    if (!apiClient) return;
    
    try {
      setJobId(id);
      setResults(null);
      setError(null);
      setIsPolling(true);
      
      const job = await apiClient.getJobStatus(id);
      setJobStatus(job.status);
      
      if (job.status === "completed") {
        setIsPolling(false);
        const resultsData = await apiClient.getJobResults(id);
        setResults(resultsData.results);
        // Switch to results view
        setActiveTab("results");
      } else if (job.status === "pending" || job.status === "running") {
        setActiveTab("results");
        pollJobStatus(id);
      } else {
        setIsPolling(false);
        setError(`Job is ${job.status}, cannot view results yet`);
      }
    } catch (err) {
      setIsPolling(false);
      setError(`Failed to load job results: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Get status label with color
  const getStatusLabel = (status: string) => {
    let bgColor = "bg-gray-100 text-gray-800";
    
    switch (status) {
      case "completed":
        bgColor = "bg-green-100 text-green-800";
        break;
      case "pending":
        bgColor = "bg-yellow-100 text-yellow-800";
        break;
      case "running":
        bgColor = "bg-blue-100 text-blue-800";
        break;
      case "failed":
        bgColor = "bg-red-100 text-red-800";
        break;
    }
    
    return (
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${bgColor}`}>
        {status}
      </span>
    );
  };
  
  return (
    <Card className="border shadow-sm">
      <CardContent className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="scrape" className="text-sm sm:text-base">Single Scrape</TabsTrigger>
            <TabsTrigger value="batch" className="text-sm sm:text-base">Batch Scrape</TabsTrigger>
            <TabsTrigger value="map" className="text-sm sm:text-base">Site Map</TabsTrigger>
            <TabsTrigger value="jobs" className="text-sm sm:text-base">My Jobs</TabsTrigger>
          </TabsList>
          
          {successMessage && (
            <div className="mb-4 p-3 border border-green-200 rounded-md bg-green-50 text-green-800">
              <div className="flex items-center">
                <svg className="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>{successMessage}</span>
              </div>
            </div>
          )}
          
          {jobId && jobStatus && activeTab === "results" && (
            <div className="flex items-center justify-between mb-4 bg-muted/30 p-3 rounded-md">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">Job ID: {jobId.substring(0, 8)}...</span>
                {getStatusLabel(jobStatus)}
              </div>
              {isPolling && (
                <div className="flex items-center text-sm text-muted-foreground">
                  <svg className="w-4 h-4 mr-2 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </div>
              )}
            </div>
          )}
          
          {error && (
            <div className="mb-6 p-4 border border-red-200 rounded-md bg-red-50 text-red-800">
              <div className="flex items-start">
                <svg className="h-5 w-5 mr-2 mt-0.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium">Error</h4>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          <TabsContent value="scrape" className="mt-0">
            <ScrapeForm
              onStartScraping={handleStartScraping}
              setError={setError}
            />
          </TabsContent>
          
          <TabsContent value="batch" className="mt-0">
            <BatchForm
              onStartBatch={handleStartScraping}
              setError={setError}
            />
          </TabsContent>
          
          <TabsContent value="map" className="mt-0">
            {showMapResults ? (
              <MapResults 
                links={mapLinks}
                baseUrl={mapBaseUrl}
                onStartBatch={handleStartScraping}
                onBack={handleMapBack}
                setError={setError}
              />
            ) : (
              <SiteMap
                onMapComplete={handleMapComplete}
                setError={setError}
              />
            )}
          </TabsContent>
          
          <TabsContent value="jobs" className="mt-0">
            <JobList
              onViewResults={handleViewResults}
              setError={setError}
            />
          </TabsContent>
          
          <TabsContent value="results" className="mt-0">
            {isPolling && !results && (
              <div className="flex flex-col items-center justify-center py-12">
                <svg className="w-12 h-12 mb-4 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-lg font-medium">Processing your request...</p>
                <p className="text-sm text-muted-foreground mt-2">This may take a moment depending on the site complexity</p>
              </div>
            )}
            
            {results && (
              <ResultsView
                results={results}
                jobId={jobId || ""}
                status={jobStatus || ""}
              />
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default Scraper; 