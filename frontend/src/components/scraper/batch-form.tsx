"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import { 
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/lib/auth";
import { createApiClient, ScrapeOptions } from "@/lib/api";

interface BatchFormProps {
  onStartBatch: (jobId: string, status: string) => void;
  setError: (error: string | null) => void;
}

export function BatchForm({ onStartBatch, setError }: BatchFormProps) {
  const { apiKey } = useAuth();
  const [urls, setUrls] = useState("");
  const [loading, setLoading] = useState(false);
  const [formats, setFormats] = useState<string[]>(["markdown", "html"]);
  
  // Extraction options
  const [extractEnabled, setExtractEnabled] = useState(false);
  const [extractPrompt, setExtractPrompt] = useState("");
  const [extractSchema, setExtractSchema] = useState("");
  
  // Proxy settings
  const [proxyEnabled, setProxyEnabled] = useState(false);
  const [proxyType, setProxyType] = useState<"basic" | "stealth">("basic");
  const [retryWithStealth, setRetryWithStealth] = useState(true);

  // Initialize API client
  const apiClient = createApiClient(apiKey || "");

  // Handle form submission
  const handleSubmit = async () => {
    if (!apiKey) {
      setError("Please add your API keys in the profile page");
      return;
    }
    
    if (!urls.trim()) {
      setError("At least one URL is required");
      return;
    }
    
    // Parse URLs (split by new line and filter empty lines)
    const urlList = urls
      .split("\n")
      .map(url => url.trim())
      .filter(url => url.length > 0);
    
    if (urlList.length === 0) {
      setError("At least one valid URL is required");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Build options
      const options: ScrapeOptions & Record<string, unknown> = {
        formats
      };
      
      // Add extraction options if enabled
      if (extractEnabled) {
        if (extractPrompt) {
          options.extract_prompt = extractPrompt;
        }
        
        if (extractSchema) {
          try {
            options.extract_schema = JSON.parse(extractSchema);
          } catch {
            setError("Invalid JSON schema");
            setLoading(false);
            return;
          }
        }
        
        // Add JSON format if using extraction
        if (!options.formats?.includes("json")) {
          options.formats = [...(options.formats || []), "json"];
        }
      }
      
      // Add proxy settings if enabled
      if (proxyEnabled) {
        options.proxy = proxyType;
        options.retry_with_stealth = retryWithStealth;
      }
      
      const response = await apiClient.startBatchScraping(urlList, options);
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
        <CardTitle>Batch URL Scraper</CardTitle>
        <CardDescription>
          Process multiple URLs simultaneously by entering one URL per line
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <label htmlFor="urls" className="text-sm font-medium">URLs (one per line)</label>
            <Textarea
              id="urls"
              placeholder="https://example.com/page1
https://example.com/page2
https://example.com/page3"
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              className="min-h-[150px] font-mono text-sm"
            />
            <p className="text-sm text-muted-foreground">
              Enter each URL on a new line. The scraper will process them in parallel.
            </p>
          </div>
          
          <div className="grid gap-2">
            <label htmlFor="formats" className="text-sm font-medium">Output Formats</label>
            <div className="flex flex-wrap gap-2">
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox"
                  id="format-markdown" 
                  checked={formats.includes("markdown")}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormats([...formats, "markdown"]);
                    } else {
                      setFormats(formats.filter(f => f !== "markdown"));
                    }
                  }}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label htmlFor="format-markdown" className="text-sm">Markdown</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox"
                  id="format-html" 
                  checked={formats.includes("html")}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormats([...formats, "html"]);
                    } else {
                      setFormats(formats.filter(f => f !== "html"));
                    }
                  }}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label htmlFor="format-html" className="text-sm">HTML</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox"
                  id="format-json" 
                  checked={formats.includes("json")}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormats([...formats, "json"]);
                    } else {
                      setFormats(formats.filter(f => f !== "json"));
                    }
                  }}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label htmlFor="format-json" className="text-sm">JSON</label>
              </div>
            </div>
          </div>
          
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="extraction-options">
              <AccordionTrigger>Structured Data Extraction</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-extraction" 
                      checked={extractEnabled}
                      onChange={(e) => setExtractEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-extraction" className="text-sm">Enable structured data extraction</label>
                  </div>
                  
                  {extractEnabled && (
                    <>
                      <div className="grid gap-2 pt-2">
                        <label htmlFor="extract-prompt" className="text-sm font-medium">
                          Extraction Prompt
                        </label>
                        <Textarea
                          id="extract-prompt"
                          placeholder="Describe what data to extract from the pages"
                          value={extractPrompt}
                          onChange={(e) => setExtractPrompt(e.target.value)}
                          className="min-h-[100px]"
                        />
                        <p className="text-xs text-muted-foreground">
                          Example: &quot;Extract product names, prices, and descriptions from these e-commerce pages&quot;
                        </p>
                      </div>
                      
                      <div className="grid gap-2 pt-2">
                        <label htmlFor="extract-schema" className="text-sm font-medium">
                          JSON Schema (Optional)
                        </label>
                        <Textarea
                          id="extract-schema"
                          placeholder='{"properties": {"product": {"type": "string"}, "price": {"type": "number"}}}'
                          value={extractSchema}
                          onChange={(e) => setExtractSchema(e.target.value)}
                          className="min-h-[100px] font-mono text-sm"
                        />
                        <p className="text-xs text-muted-foreground">
                          Provide a JSON schema for structured extraction (must be valid JSON)
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="proxy-settings">
              <AccordionTrigger>Proxy Settings</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-proxy" 
                      checked={proxyEnabled}
                      onChange={(e) => setProxyEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-proxy" className="text-sm">Enable proxy</label>
                  </div>
                  
                  {proxyEnabled && (
                    <div className="space-y-3 pl-6">
                      <div className="grid gap-2">
                        <label className="text-xs">Proxy Type</label>
                        <Select
                          value={proxyType}
                          onValueChange={(value: "basic" | "stealth") => setProxyType(value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select proxy type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="basic">Basic</SelectItem>
                            <SelectItem value="stealth">Stealth (5x credit cost)</SelectItem>
                          </SelectContent>
                        </Select>
                        <p className="text-xs text-muted-foreground">
                          Note: Stealth proxy costs 5 credits per URL
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <input 
                          type="checkbox"
                          id="retry-stealth" 
                          checked={retryWithStealth}
                          onChange={(e) => setRetryWithStealth(e.target.checked)}
                          className="h-4 w-4 rounded border-gray-300"
                        />
                        <label htmlFor="retry-stealth" className="text-sm">Retry with stealth if basic fails</label>
                      </div>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          className="w-full" 
          onClick={handleSubmit}
          disabled={loading || !apiKey || !urls.trim()}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing Batch...
            </>
          ) : (
            "Start Batch Scraping"
          )}
        </Button>
      </CardFooter>
    </Card>
  );
} 