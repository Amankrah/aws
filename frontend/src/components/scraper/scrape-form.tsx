"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, PlusCircle, X } from "lucide-react";
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
import { createApiClient, ScrapeOptions, AgentOptions } from "@/lib/api";

// Extend the AgentOptions interface to include prompt property
interface ExtendedAgentOptions extends AgentOptions {
  prompt?: string;
}

interface PageAction {
  type: string;
  selector?: string;
  milliseconds?: number;
  text?: string;
  key?: string;
}

interface LocationSettings {
  country: string;
  languages?: string[];
}

interface ScrapeFormProps {
  onStartScraping: (jobId: string, status: string) => void;
  setError: (error: string | null) => void;
}

export function ScrapeForm({ onStartScraping, setError }: ScrapeFormProps) {
  const { apiKey } = useAuth();
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [advancedOptions, setAdvancedOptions] = useState<ScrapeOptions>({
    formats: ["markdown", "html"],
    max_depth: 2,
    allow_external_links: false,
    only_main_content: true,
    parse_pdf: true,
  });

  // Agent options
  const [agentEnabled, setAgentEnabled] = useState(false);
  const [agentPrompt, setAgentPrompt] = useState("");
  
  // Extraction options
  const [extractEnabled, setExtractEnabled] = useState(false);
  const [extractPrompt, setExtractPrompt] = useState("");
  const [extractSchema, setExtractSchema] = useState("");
  
  // Page actions
  const [actionsEnabled, setActionsEnabled] = useState(false);
  const [pageActions, setPageActions] = useState<PageAction[]>([]);
  
  // Location settings
  const [locationEnabled, setLocationEnabled] = useState(false);
  const [location, setLocation] = useState<LocationSettings>({ country: "US" });
  const [languages, setLanguages] = useState("");
  
  // Proxy settings
  const [proxyEnabled, setProxyEnabled] = useState(false);
  const [proxyType, setProxyType] = useState<"basic" | "stealth">("basic");
  const [retryWithStealth, setRetryWithStealth] = useState(true);
  
  // Content filtering
  const [filteringEnabled, setFilteringEnabled] = useState(false);
  const [includeTags, setIncludeTags] = useState("");
  const [excludeTags, setExcludeTags] = useState("");
  const [waitTime, setWaitTime] = useState(0);
  const [timeout, setTimeout] = useState(30000);

  // Initialize API client
  const apiClient = createApiClient(apiKey || "");

  // Update advanced options
  const updateOption = (key: keyof ScrapeOptions, value: unknown) => {
    setAdvancedOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  // Add a new page action
  const addPageAction = () => {
    setPageActions([...pageActions, { type: "wait", milliseconds: 1000 }]);
  };
  
  // Update a page action
  const updatePageAction = (index: number, field: keyof PageAction, value: string | number | boolean | undefined) => {
    const updatedActions = [...pageActions];
    updatedActions[index] = { ...updatedActions[index], [field]: value };
    setPageActions(updatedActions);
  };
  
  // Remove a page action
  const removePageAction = (index: number) => {
    const updatedActions = [...pageActions];
    updatedActions.splice(index, 1);
    setPageActions(updatedActions);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!apiKey) {
      setError("Please add your API keys in the profile page");
      return;
    }
    
    if (!query) {
      setError("Search query is required");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Build complete options object
      const scraperOptions: ScrapeOptions & Record<string, unknown> = {
        ...advancedOptions
      };
      
      // Add agent options if enabled
      if (agentEnabled) {
        const agent: ExtendedAgentOptions = {
          model: "FIRE-1",
          thinking_enabled: true,
          thinking_budget: 60
        };
        
        if (agentPrompt) {
          agent.prompt = agentPrompt;
        }
        
        scraperOptions.agent = agent as AgentOptions;
      }
      
      // Add extraction options if enabled
      if (extractEnabled) {
        if (extractPrompt) {
          scraperOptions.extract_prompt = extractPrompt;
        }
        
        if (extractSchema) {
          try {
            scraperOptions.extract_schema = JSON.parse(extractSchema);
          } catch {
            setError("Invalid JSON schema");
            setLoading(false);
            return;
          }
        }
        
        // Add JSON format if using extraction
        if (!scraperOptions.formats?.includes("json")) {
          scraperOptions.formats = [...(scraperOptions.formats || []), "json"];
        }
      }
      
      // Add page actions if enabled
      if (actionsEnabled && pageActions.length > 0) {
        scraperOptions.actions = pageActions;
      }
      
      // Add location settings if enabled
      if (locationEnabled) {
        const locationConfig: LocationSettings = {
          country: location.country
        };
        
        if (languages) {
          locationConfig.languages = languages.split(',').map(lang => lang.trim());
        }
        
        scraperOptions.location = locationConfig;
      }
      
      // Add proxy settings if enabled
      if (proxyEnabled) {
        scraperOptions.proxy = proxyType;
        scraperOptions.retry_with_stealth = retryWithStealth;
      }
      
      // Add content filtering if enabled
      if (filteringEnabled) {
        if (includeTags) {
          scraperOptions.include_tags = includeTags.split(',').map(tag => tag.trim());
        }
        
        if (excludeTags) {
          scraperOptions.exclude_tags = excludeTags.split(',').map(tag => tag.trim());
        }
        
        scraperOptions.wait_for = waitTime;
        scraperOptions.timeout = timeout;
      }
      
      const response = await apiClient.startScraping(query, domain || undefined, scraperOptions);
      onStartScraping(response.job_id, response.status);
    } catch (err) {
      setError(`Failed to start scraping: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
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
          
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="crawl-options">
              <AccordionTrigger>Crawling Options</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="parse-pdf" 
                      checked={advancedOptions.parse_pdf}
                      onChange={(e) => 
                        updateOption("parse_pdf", e.target.checked)
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
                        updateOption("only_main_content", e.target.checked)
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
                        updateOption("allow_external_links", e.target.checked)
                      }
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="allow-external-links" className="text-sm">Follow external links</label>
                  </div>
                  
                  <div className="grid gap-2 pt-2">
                    <label htmlFor="max-depth" className="text-sm font-medium">Maximum Crawl Depth</label>
                    <Input
                      id="max-depth"
                      type="number"
                      min="1"
                      max="10"
                      value={advancedOptions.max_depth}
                      onChange={(e) => 
                        updateOption("max_depth", parseInt(e.target.value) || 2)
                      }
                    />
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="page-actions">
              <AccordionTrigger>Page Interactions</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-actions" 
                      checked={actionsEnabled}
                      onChange={(e) => setActionsEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-actions" className="text-sm">Enable page interactions</label>
                  </div>
                  
                  {actionsEnabled && (
                    <div className="space-y-4">
                      {pageActions.map((action, index) => (
                        <div key={index} className="border p-3 rounded-md space-y-3">
                          <div className="flex justify-between items-center">
                            <h4 className="text-sm font-medium">Action {index + 1}</h4>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => removePageAction(index)}
                              className="h-6 w-6 p-0"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                          
                          <div className="grid gap-2">
                            <label className="text-xs">Type</label>
                            <Select
                              value={action.type}
                              onValueChange={(value) => updatePageAction(index, 'type', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select action type" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="wait">Wait</SelectItem>
                                <SelectItem value="click">Click</SelectItem>
                                <SelectItem value="write">Write Text</SelectItem>
                                <SelectItem value="press">Press Key</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          
                          {action.type === 'wait' && (
                            <div className="grid gap-2">
                              <label className="text-xs">Wait Time (ms)</label>
                              <Input
                                type="number"
                                value={action.milliseconds || 1000}
                                onChange={(e) => updatePageAction(
                                  index, 
                                  'milliseconds', 
                                  parseInt(e.target.value) || 1000
                                )}
                                className="text-sm"
                              />
                            </div>
                          )}
                          
                          {(action.type === 'click' || action.type === 'write') && (
                            <div className="grid gap-2">
                              <label className="text-xs">CSS Selector</label>
                              <Input
                                value={action.selector || ''}
                                onChange={(e) => updatePageAction(
                                  index, 
                                  'selector', 
                                  e.target.value
                                )}
                                placeholder="e.g., button.submit, #search-input"
                                className="text-sm"
                              />
                            </div>
                          )}
                          
                          {action.type === 'write' && (
                            <div className="grid gap-2">
                              <label className="text-xs">Text to Write</label>
                              <Input
                                value={action.text || ''}
                                onChange={(e) => updatePageAction(
                                  index, 
                                  'text', 
                                  e.target.value
                                )}
                                className="text-sm"
                              />
                            </div>
                          )}
                          
                          {action.type === 'press' && (
                            <div className="grid gap-2">
                              <label className="text-xs">Key to Press</label>
                              <Select
                                value={action.key || 'Enter'}
                                onValueChange={(value) => updatePageAction(index, 'key', value)}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select key" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="Enter">Enter</SelectItem>
                                  <SelectItem value="Tab">Tab</SelectItem>
                                  <SelectItem value="Escape">Escape</SelectItem>
                                  <SelectItem value="ArrowDown">Arrow Down</SelectItem>
                                  <SelectItem value="ArrowUp">Arrow Up</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          )}
                        </div>
                      ))}
                      
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={addPageAction}
                        className="w-full flex items-center justify-center"
                      >
                        <PlusCircle className="mr-2 h-4 w-4" />
                        Add Action
                      </Button>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="location-proxy">
              <AccordionTrigger>Regional & Security</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <h4 className="text-sm font-medium">Location Settings</h4>
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-location" 
                      checked={locationEnabled}
                      onChange={(e) => setLocationEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-location" className="text-sm">Enable location settings</label>
                  </div>
                  
                  {locationEnabled && (
                    <div className="space-y-3 pl-6">
                      <div className="grid gap-2">
                        <label className="text-xs">Country</label>
                        <Select
                          value={location.country}
                          onValueChange={(value) => setLocation({...location, country: value})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select country" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="US">United States</SelectItem>
                            <SelectItem value="GB">United Kingdom</SelectItem>
                            <SelectItem value="CA">Canada</SelectItem>
                            <SelectItem value="AU">Australia</SelectItem>
                            <SelectItem value="DE">Germany</SelectItem>
                            <SelectItem value="FR">France</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="grid gap-2">
                        <label className="text-xs">Languages (comma-separated)</label>
                        <Input
                          value={languages}
                          onChange={(e) => setLanguages(e.target.value)}
                          placeholder="e.g., en,es,fr"
                          className="text-sm"
                        />
                      </div>
                    </div>
                  )}
                  
                  <div className="border-t my-4"></div>
                  
                  <h4 className="text-sm font-medium">Proxy Settings</h4>
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
            
            <AccordionItem value="content-filtering">
              <AccordionTrigger>Content Filtering</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-filtering" 
                      checked={filteringEnabled}
                      onChange={(e) => setFilteringEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-filtering" className="text-sm">Enable advanced content filtering</label>
                  </div>
                  
                  {filteringEnabled && (
                    <div className="space-y-3 pl-6">
                      <div className="grid gap-2">
                        <label className="text-xs">Include Tags (comma-separated)</label>
                        <Input
                          value={includeTags}
                          onChange={(e) => setIncludeTags(e.target.value)}
                          placeholder="e.g., article, .content, #main"
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">
                          HTML tags, CSS classes, or IDs to include in the extraction
                        </p>
                      </div>
                      
                      <div className="grid gap-2">
                        <label className="text-xs">Exclude Tags (comma-separated)</label>
                        <Input
                          value={excludeTags}
                          onChange={(e) => setExcludeTags(e.target.value)}
                          placeholder="e.g., nav, .sidebar, #comments"
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">
                          HTML tags, CSS classes, or IDs to exclude from extraction
                        </p>
                      </div>
                      
                      <div className="grid gap-2">
                        <label className="text-xs">Wait Time (ms)</label>
                        <Input
                          type="number"
                          value={waitTime}
                          onChange={(e) => setWaitTime(parseInt(e.target.value) || 0)}
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">
                          Time to wait for dynamic content to load
                        </p>
                      </div>
                      
                      <div className="grid gap-2">
                        <label className="text-xs">Timeout (ms)</label>
                        <Input
                          type="number"
                          value={timeout}
                          onChange={(e) => setTimeout(parseInt(e.target.value) || 30000)}
                          className="text-sm"
                        />
                        <p className="text-xs text-muted-foreground">
                          Maximum time to wait for page response
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="agent-options">
              <AccordionTrigger>AI Agent Options</AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center space-x-2">
                    <input 
                      type="checkbox"
                      id="enable-agent" 
                      checked={agentEnabled}
                      onChange={(e) => setAgentEnabled(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor="enable-agent" className="text-sm">Enable AI navigation agent</label>
                  </div>
                  
                  {agentEnabled && (
                    <div className="grid gap-2 pt-2">
                      <label htmlFor="agent-prompt" className="text-sm font-medium">
                        Agent Instructions (Optional)
                      </label>
                      <Textarea
                        id="agent-prompt"
                        placeholder="Provide detailed instructions for the agent on how to navigate and interact with webpages"
                        value={agentPrompt}
                        onChange={(e) => setAgentPrompt(e.target.value)}
                        className="min-h-[100px]"
                      />
                      <p className="text-xs text-muted-foreground">
                        Use this to guide the FIRE-1 agent on how to navigate complex websites or perform specific interactions
                      </p>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
            
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
                          Example: &quot;Extract product names, prices, and descriptions from this e-commerce page&quot;
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
          </Accordion>
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
  );
} 