"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { 
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { useAuth } from "@/lib/auth";
import { createApiClient } from "@/lib/api";

interface MapResponse {
  status: string;
  links: string[];
}

interface SiteMapProps {
  setError: (error: string | null) => void;
  onMapComplete: (links: string[], url: string) => void;
}

export function SiteMap({ setError, onMapComplete }: SiteMapProps) {
  const { apiKey } = useAuth();
  const [url, setUrl] = useState("");
  const [search, setSearch] = useState("");
  const [includeSubdomains, setIncludeSubdomains] = useState(false);
  const [limit, setLimit] = useState(100);
  const [loading, setLoading] = useState(false);

  // Initialize API client
  const apiClient = createApiClient(apiKey || "");

  // Handle form submission
  const handleSubmit = async () => {
    if (!apiKey) {
      setError("Please add your API keys in the profile page");
      return;
    }
    
    if (!url) {
      setError("URL is required");
      return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError("URL must start with http:// or https://");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const options = {
        search: search || undefined,
        limit,
        include_subdomains: includeSubdomains,
      };
      
      const response = await apiClient.mapWebsite(url, options);
      
      if (response.job_id) {
        // This will need to poll for job completion in a real implementation
        // For now, we'll simulate completion with a direct API call
        const mapResult = await simulateMapResult(url);
        onMapComplete(mapResult.links, url);
      }
    } catch (err) {
      setError(`Failed to map website: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };
  
  // This function simulates getting the map result
  // In a real implementation, you would poll the job status
  const simulateMapResult = async (url: string): Promise<MapResponse> => {
    // This is a placeholder, in reality you would poll the job status API
    // and then fetch the actual links when the job is complete
    return {
      status: "completed",
      links: [
        `${url}/page1`,
        `${url}/page2`,
        `${url}/about`,
        `${url}/contact`,
        `${url}/products/1`,
        `${url}/products/2`,
      ]
    };
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Website Mapper</CardTitle>
        <CardDescription>
          Map the structure of a website to discover pages for scraping
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <label htmlFor="url" className="text-sm font-medium">Website URL</label>
            <Input
              id="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Provide the root URL of the website you want to map
            </p>
          </div>
          
          <div className="grid gap-2">
            <label htmlFor="search" className="text-sm font-medium">Search Term (Optional)</label>
            <Input
              id="search"
              placeholder="e.g., products, contact"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Optionally filter URLs by relevance to a search term
            </p>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label htmlFor="limit" className="text-sm font-medium">Link Limit</label>
              <Input
                id="limit"
                type="number"
                placeholder="100"
                min="1"
                max="500"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
              />
            </div>
            
            <div className="flex items-center space-x-2 self-end">
              <input 
                type="checkbox"
                id="include-subdomains" 
                checked={includeSubdomains}
                onChange={(e) => setIncludeSubdomains(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <label htmlFor="include-subdomains" className="text-sm">Include subdomains</label>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          className="w-full" 
          onClick={handleSubmit}
          disabled={loading || !apiKey || !url}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Mapping Website...
            </>
          ) : (
            "Map Website"
          )}
        </Button>
      </CardFooter>
    </Card>
  );
} 