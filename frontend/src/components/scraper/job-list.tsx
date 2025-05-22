"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { 
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { useAuth } from "@/lib/auth";
import { createApiClient, ScrapeJob } from "@/lib/api";

interface JobListProps {
  onViewResults: (jobId: string) => void;
  setError: (error: string | null) => void;
}

export function JobList({ onViewResults, setError }: JobListProps) {
  const { apiKey } = useAuth();
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Initialize API client
  const apiClient = apiKey ? createApiClient(apiKey) : null;
  
  // Fetch job list
  const fetchJobs = useCallback(async () => {
    if (!apiClient) return;
    
    try {
      setLoading(true);
      const fetchedJobs = await apiClient.listJobs();
      setJobs(fetchedJobs);
    } catch (err) {
      setError(`Failed to fetch jobs: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  }, [apiClient, setError]);
  
  // Fetch jobs on initial render
  useEffect(() => {
    if (apiClient) {
      fetchJobs();
    }
  }, [apiClient, fetchJobs]);
  
  // Delete a job
  const deleteJob = async (jobId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (!apiClient) return;
    
    try {
      await apiClient.deleteJob(jobId);
      // Refresh job list
      fetchJobs();
    } catch (err) {
      setError(`Failed to delete job: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'running':
        return 'bg-blue-500';
      default:
        return 'bg-yellow-500';
    }
  };
  
  // Load job results
  const handleViewResults = (jobId: string) => {
    onViewResults(jobId);
  };
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle>My Scraping Jobs</CardTitle>
          <CardDescription>
            View and manage your previous scraping jobs
          </CardDescription>
        </div>
        <Button 
          variant="outline"
          size="sm"
          onClick={fetchJobs}
          disabled={loading}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Refresh"}
        </Button>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center p-4">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : jobs.length > 0 ? (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div 
                key={job.job_id} 
                className="border p-4 rounded-md hover:bg-slate-50 dark:hover:bg-slate-900/20 cursor-pointer"
                onClick={() => job.status === 'completed' && handleViewResults(job.job_id)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">{job.query}</h3>
                    <p className="text-sm text-muted-foreground">
                      Created: {new Date(job.created_at).toLocaleString()}
                    </p>
                    <div className="flex items-center mt-1">
                      <span 
                        className={`inline-block w-2 h-2 rounded-full mr-2 ${getStatusColor(job.status)}`}
                      />
                      <span className="text-sm">{job.status}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleViewResults(job.job_id)}
                      disabled={job.status !== 'completed'}
                    >
                      View
                    </Button>
                    <Button 
                      size="sm" 
                      variant="destructive"
                      onClick={(e) => deleteJob(job.job_id, e)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <p>No jobs found. Start a new scraping job to see results here.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 