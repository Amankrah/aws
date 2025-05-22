'use client';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 md:py-28 lg:py-32 bg-gradient-to-br from-background via-background to-muted border-b">
          <div className="absolute inset-0 bg-grid-small-black/[0.02] -z-10" />
          <div className="absolute inset-0 bg-gradient-to-b from-background to-transparent -z-10" />
          
          <div className="container px-4 md:px-6 mx-auto">
            <div className="grid gap-10 lg:grid-cols-2 lg:gap-16 items-center">
              <div className="flex flex-col justify-center space-y-6 max-w-2xl">
                <div className="space-y-2">
                  <div className="inline-block px-3 py-1 mb-4 text-sm font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                    Intelligent Web Scraping
                  </div>
                  <h1 className="text-4xl font-bold tracking-tight sm:text-5xl xl:text-6xl">
                    Universal Agentic 
                    <span className="text-blue-600 dark:text-blue-500"> Scraper</span>
                  </h1>
                  <p className="text-xl text-muted-foreground mt-4">
                    Extract structured data from any website with AI-powered analysis and comprehensive web coverage.
                  </p>
                </div>
                <div className="flex flex-col gap-3 min-[400px]:flex-row mt-4">
                  {isAuthenticated ? (
                    <Link href="/scraper" passHref>
                      <Button size="lg" className="flex-1 rounded-xl">Start Scraping</Button>
                    </Link>
                  ) : (
                    <Link href="/auth" passHref>
                      <Button size="lg" className="flex-1 rounded-xl">Get Started</Button>
                    </Link>
                  )}
                  <Link href="/docs" passHref>
                    <Button variant="outline" size="lg" className="flex-1 rounded-xl">Documentation</Button>
                  </Link>
                </div>
                
                <div className="flex items-center mt-8 text-sm text-muted-foreground">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-4 w-4">
                    <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"></path>
                    <path d="m9 12 2 2 4-4"></path>
                  </svg>
                  <span className="mr-4">Privacy-focused</span>
                  
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-4 w-4">
                    <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"></path>
                    <path d="m9 12 2 2 4-4"></path>
                  </svg>
                  <span>Advanced AI models</span>
                </div>
              </div>
              
              <div className="flex flex-col justify-center">
                <Card className="overflow-hidden border-2 shadow-xl">
                  <CardHeader className="bg-gradient-to-b from-muted/50 to-background pb-8">
                    <CardTitle className="text-2xl">Scraping Made Easy</CardTitle>
                    <CardDescription>
                      Powerful tools to extract, analyze and organize web data
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-4">
                        <div className="rounded-full bg-blue-100 dark:bg-blue-900/30 p-2">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-blue-600 dark:text-blue-400">
                            <path d="M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"></path>
                            <path d="M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3"></path>
                            <path d="M4 12H2"></path>
                            <path d="M10 12H8"></path>
                            <path d="M16 12h-2"></path>
                            <path d="M22 12h-2"></path>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">Full Website Crawling</h3>
                          <p className="text-sm text-muted-foreground">Extract data from entire websites with a single request</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="rounded-full bg-blue-100 dark:bg-blue-900/30 p-2">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-blue-600 dark:text-blue-400">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="m4.9 4.9 14.2 14.2"></path>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">Anti-Bot Bypassing</h3>
                          <p className="text-sm text-muted-foreground">Access sites with anti-scraping protection</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div className="rounded-full bg-blue-100 dark:bg-blue-900/30 p-2">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-blue-600 dark:text-blue-400">
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                            <polyline points="3.29 7 12 12 20.71 7"></polyline>
                            <line x1="12" x2="12" y1="22" y2="12"></line>
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">AI-Powered Analysis</h3>
                          <p className="text-sm text-muted-foreground">Claude 3.7 analyzes content for valuable insights</p>
                        </div>
                      </div>
                      
                      <div className="mt-6 flex justify-center">
                        <Link href="/scraper">
                          <Button className="w-full">
                            {isAuthenticated ? "Go to Scraper" : "Sign In to Start"}
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 md:py-24">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2 max-w-3xl">
                <div className="inline-block px-3 py-1 mb-2 text-sm font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                  Key Features
                </div>
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                  Powerful Scraping Platform
                </h2>
                <p className="text-lg text-muted-foreground max-w-[900px] mx-auto">
                  Our platform combines Claude 3.7 and Firecrawl for intelligent data extraction and analysis
                </p>
              </div>
            </div>
            
            <div className="mx-auto grid max-w-6xl gap-8 py-12 md:grid-cols-2 lg:grid-cols-3">
              <Card className="group hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
                <CardContent className="p-6 flex flex-col items-start">
                  <div className="rounded-lg p-3 bg-blue-100 dark:bg-blue-900/30 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-blue-600 dark:text-blue-400">
                      <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
                      <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
                      <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"></path>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold">AI-Powered Analysis</h3>
                  <p className="text-muted-foreground mt-2">
                    Claude 3.7 intelligently analyzes and summarizes web content, extracting key insights and structured data.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="group hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
                <CardContent className="p-6 flex flex-col items-start">
                  <div className="rounded-lg p-3 bg-blue-100 dark:bg-blue-900/30 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-blue-600 dark:text-blue-400">
                      <rect width="18" height="18" x="3" y="3" rx="2"></rect>
                      <path d="M7 7h10"></path>
                      <path d="M7 12h10"></path>
                      <path d="M7 17h10"></path>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold">Robust Web Extraction</h3>
                  <p className="text-muted-foreground mt-2">
                    Firecrawl handles JavaScript, anti-bot measures, and complex websites to provide comprehensive data coverage.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="group hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
                <CardContent className="p-6 flex flex-col items-start">
                  <div className="rounded-lg p-3 bg-blue-100 dark:bg-blue-900/30 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-blue-600 dark:text-blue-400">
                      <path d="M3 3v18h18"></path>
                      <rect width="4" height="7" x="7" y="10" rx="1"></rect>
                      <rect width="4" height="12" x="15" y="5" rx="1"></rect>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold">Structured Data Extraction</h3>
                  <p className="text-muted-foreground mt-2">
                    Extract specific data points according to custom schemas, enabling precise data collection for your needs.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
        
        {/* CTA Section */}
        <section className="bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-blue-950/20 dark:via-background dark:to-blue-950/20 py-16 border-t">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="flex flex-col items-center text-center max-w-3xl mx-auto space-y-6">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Ready to extract valuable data?
              </h2>
              <p className="text-lg text-muted-foreground">
                Start collecting structured data from any website with our powerful AI-driven scraping platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mt-2">
                {isAuthenticated ? (
                  <Link href="/scraper">
                    <Button size="lg" className="px-8 rounded-xl">Go to Scraper</Button>
                  </Link>
                ) : (
                  <Link href="/auth">
                    <Button size="lg" className="px-8 rounded-xl">Get Started Now</Button>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
