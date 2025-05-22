import { Scraper } from "@/components/scraper";

export const metadata = {
  title: 'Universal Agentic Web Scraper | Extract Data with AI',
  description: 'Advanced web scraper powered by AI to extract structured data, map websites, and batch process URLs',
};

export default function ScraperPage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-3 mb-8">
          <h1 className="text-4xl font-bold">Universal Agentic Web Scraper</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Extract structured data from any website with our AI-powered scraper
          </p>
        </div>
        
        <div className="grid gap-6 mb-8 text-sm sm:grid-cols-3">
          <div className="flex flex-col items-center p-4 bg-muted/40 rounded-lg text-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M20 7h-3a2 2 0 0 1-2-2V2" />
                <path d="M9 18a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h7l4 4v10a2 2 0 0 1-2 2Z" />
                <path d="M3 7v10a2 2 0 0 0 2 2h4" />
                <path d="M12 18v4" />
                <path d="M16 18v4" />
              </svg>
            </div>
            <h3 className="font-medium mb-1">Single Page Scraper</h3>
            <p className="text-muted-foreground">Extract content from individual web pages with precise control</p>
          </div>
          
          <div className="flex flex-col items-center p-4 bg-muted/40 rounded-lg text-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <path d="M7 7h10" />
                <path d="M7 12h2" />
                <path d="M7 17h6" />
              </svg>
            </div>
            <h3 className="font-medium mb-1">Batch Processing</h3>
            <p className="text-muted-foreground">Process multiple URLs at once for efficient data extraction</p>
          </div>
          
          <div className="flex flex-col items-center p-4 bg-muted/40 rounded-lg text-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16" />
                <path d="M21 21H3" />
                <path d="M7 10h0" />
                <path d="M17 14h0" />
                <path d="M17 8h0" />
                <path d="M7 18h0" />
                <path d="M12 13h0" />
              </svg>
            </div>
            <h3 className="font-medium mb-1">Site Mapping</h3>
            <p className="text-muted-foreground">Automatically discover and analyze all pages on a website</p>
          </div>
        </div>
        
        <Scraper />
        
        <div className="mt-10 bg-muted/30 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">How to Use the Scraper</h2>
          <ul className="space-y-3 list-disc pl-5">
            <li><strong>Single Scrape:</strong> Enter a URL and optional query to extract specific content from a web page.</li>
            <li><strong>Batch Scrape:</strong> Enter multiple URLs to process them in parallel.</li>
            <li><strong>Site Map:</strong> Enter a domain to discover and map all pages on the website.</li>
            <li><strong>Advanced Options:</strong> Control extraction format, proxy settings, and more.</li>
            <li><strong>My Jobs:</strong> View and manage all your previous scraping jobs.</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 