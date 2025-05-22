"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle2, Circle } from "lucide-react";
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

interface MapResultsProps {
  links: string[];
  baseUrl: string;
  onStartBatch: (jobId: string, status: string) => void;
  onBack: () => void;
  setError: (error: string | null) => void;
}

export function MapResults({ links, baseUrl, onStartBatch, onBack, setError }: MapResultsProps) {
  const { apiKey } = useAuth();
  const [selectedLinks, setSelectedLinks] = useState<string[]>([...links]);
  const [loading, setLoading] = useState(false);

  // Initialize API client
  const apiClient = createApiClient(apiKey || "");
  
  // Toggle selection of a link
  const toggleLink = (link: string) => {
    if (selectedLinks.includes(link)) {
      setSelectedLinks(selectedLinks.filter(l => l !== link));
    } else {
      setSelectedLinks([...selectedLinks, link]);
    }
  };
  
  // Toggle selection of all links
  const toggleAll = () => {
    if (selectedLinks.length === links.length) {
      setSelectedLinks([]);
    } else {
      setSelectedLinks([...links]);
    }
  };
  
  // Handle starting batch scraping
  const handleStartBatch = async () => {
    if (!apiKey) {
      setError("Please add your API keys in the profile page");
      return;
    }
    
    if (selectedLinks.length === 0) {
      setError("Please select at least one URL to scrape");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const options = {
        formats: ["markdown", "html"]
      };
      
      const response = await apiClient.startBatchScraping(selectedLinks, options);
      onStartBatch(response.job_id, response.status);
    } catch (err) {
      setError(`Failed to start batch scraping: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Website Map Results</CardTitle>
        <CardDescription>
          {links.length} URLs found on {baseUrl}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              Select the URLs you want to scrape
            </p>
            <Button 
              variant="outline" 
              size="sm"
              onClick={toggleAll}
            >
              {selectedLinks.length === links.length ? "Deselect All" : "Select All"}
            </Button>
          </div>
          
          <div className="border rounded-md divide-y max-h-[400px] overflow-y-auto">
            {links.map((link, index) => (
              <div 
                key={index} 
                className="p-3 flex items-center hover:bg-slate-50 dark:hover:bg-slate-900/20 cursor-pointer"
                onClick={() => toggleLink(link)}
              >
                <div className="mr-3">
                  {selectedLinks.includes(link) ? (
                    <CheckCircle2 className="h-5 w-5 text-blue-500" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div className="overflow-hidden overflow-ellipsis whitespace-nowrap text-sm">
                  {link}
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex justify-between">
            <p className="text-sm">
              <span className="font-semibold">{selectedLinks.length}</span> of <span className="font-semibold">{links.length}</span> URLs selected
            </p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={onBack}
        >
          Back to Mapper
        </Button>
        <Button 
          onClick={handleStartBatch}
          disabled={loading || selectedLinks.length === 0}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            `Scrape ${selectedLinks.length} URLs`
          )}
        </Button>
      </CardFooter>
    </Card>
  );
} 