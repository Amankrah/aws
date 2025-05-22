from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, Literal
from uuid import UUID
from pydantic.json import pydantic_encoder
import json
from datetime import datetime

# Custom JSON encoder for UUID and other problematic types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if callable(obj):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Base class with custom JSON serialization
class SerializableBaseModel(BaseModel):
    def dict(self, *args, **kwargs):
        """Override dict method to ensure all values are JSON serializable"""
        result = super().dict(*args, **kwargs)
        # Convert UUID to string
        for key, value in result.items():
            if isinstance(value, UUID):
                result[key] = str(value)
        return result
        
    def json(self, *args, **kwargs):
        """Override json method to use custom encoder"""
        kwargs.setdefault("cls", CustomJSONEncoder)
        return super().json(*args, **kwargs)

class LocationSettings(SerializableBaseModel):
    country: str = Field("US", description="ISO 3166-1 alpha-2 country code")
    languages: Optional[List[str]] = Field(None, description="Preferred languages in order of priority")

class JsonExtractionConfig(SerializableBaseModel):
    json_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for extraction")
    prompt: Optional[str] = Field(None, description="Prompt for extraction without schema")
    
class PageAction(SerializableBaseModel):
    type: str = Field(..., description="Action type (wait, click, write, press, etc.)")
    selector: Optional[str] = Field(None, description="CSS selector for the element to interact with")
    milliseconds: Optional[int] = Field(None, description="Time to wait in milliseconds")
    text: Optional[str] = Field(None, description="Text to write")
    key: Optional[str] = Field(None, description="Key to press (e.g., ENTER, ESCAPE)")

class Agent(SerializableBaseModel):
    model: str = Field("FIRE-1", description="Agent model to use (currently only FIRE-1 is supported)")
    prompt: Optional[str] = Field(None, description="Detailed instructions for the agent on how to navigate and interact with the webpage")

class ScrapeRequest(SerializableBaseModel):
    query: str = Field(..., description="Search query or specific URL to scrape")
    domain: Optional[str] = Field(None, description="Optional domain to restrict the search")
    limit: Optional[int] = Field(5, description="Number of results to return")
    formats: Optional[List[str]] = Field(["markdown", "html"], description="Output formats")
    actions: Optional[List[PageAction]] = Field(None, description="Sequence of actions to perform")
    location: Optional[LocationSettings] = Field(None, description="Location settings")
    extract_schema: Optional[Dict[str, Any]] = Field(None, description="Schema for structured data extraction")
    extract_prompt: Optional[str] = Field(None, description="Prompt for extraction without schema")
    proxy: Optional[Literal["basic", "stealth"]] = Field(None, description="Proxy type (basic or stealth)")
    retry_with_stealth: Optional[bool] = Field(True, description="Whether to retry with stealth proxy if basic fails")
    agent: Optional[Agent] = Field(None, description="AI agent for intelligent navigation and interaction")
    only_main_content: Optional[bool] = Field(True, description="Whether to return only the main content of the page")
    include_tags: Optional[List[str]] = Field(None, description="HTML tags, classes and ids to include")
    exclude_tags: Optional[List[str]] = Field(None, description="HTML tags, classes and ids to exclude")
    wait_for: Optional[int] = Field(0, description="Time to wait for the page to load in milliseconds")
    timeout: Optional[int] = Field(30000, description="Maximum time to wait for the page to respond in milliseconds")
    parse_pdf: Optional[bool] = Field(True, description="Whether to parse PDF content if the URL points to a PDF")

class CrawlRequest(SerializableBaseModel):
    url: str = Field(..., description="URL to crawl")
    limit: Optional[int] = Field(10, description="Maximum number of pages to crawl")
    formats: Optional[List[str]] = Field(["markdown", "html"], description="Output formats")
    proxy: Optional[Literal["basic", "stealth"]] = Field(None, description="Proxy type (basic or stealth)")
    allow_backward_links: Optional[bool] = Field(False, description="Whether to follow links outside direct children of starting URL")
    include_paths: Optional[List[str]] = Field(None, description="Glob patterns for paths to include")
    exclude_paths: Optional[List[str]] = Field(None, description="Glob patterns for paths to exclude")
    allowed_domains: Optional[List[str]] = Field(None, description="List of domains allowed to crawl")
    webhook: Optional[str] = Field(None, description="Webhook URL to receive crawl events")
    extract_schema: Optional[Dict[str, Any]] = Field(None, description="Schema for structured data extraction")
    extract_prompt: Optional[str] = Field(None, description="Prompt for extraction without schema")
    retry_with_stealth: Optional[bool] = Field(True, description="Whether to retry with stealth proxy if basic fails")
    poll_interval: Optional[int] = Field(15, description="Interval in seconds to poll for crawl status")
    agent: Optional[Agent] = Field(None, description="AI agent for intelligent navigation and interaction")
    max_depth: Optional[int] = Field(None, description="Maximum depth to crawl relative to the entered URL")
    allow_external_links: Optional[bool] = Field(False, description="Whether to follow links that point to external domains")
    delay: Optional[int] = Field(None, description="Delay in seconds between scrapes")
    scrape_options: Optional[Dict[str, Any]] = Field(None, description="Options for the scraper to use on each page")

class WebSocketCrawlRequest(SerializableBaseModel):
    url: str = Field(..., description="URL to crawl")
    limit: Optional[int] = Field(10, description="Maximum number of pages to crawl")
    formats: Optional[List[str]] = Field(["markdown", "html"], description="Output formats")
    proxy: Optional[Literal["basic", "stealth"]] = Field(None, description="Proxy type (basic or stealth)")
    allow_backward_links: Optional[bool] = Field(False, description="Whether to follow links outside direct children of starting URL")
    include_paths: Optional[List[str]] = Field(None, description="Glob patterns for paths to include")
    exclude_paths: Optional[List[str]] = Field(None, description="Glob patterns for paths to exclude")
    allowed_domains: Optional[List[str]] = Field(None, description="List of domains allowed to crawl")

class BatchScrapeRequest(SerializableBaseModel):
    urls: List[str] = Field(..., description="List of URLs to scrape")
    formats: Optional[List[str]] = Field(["markdown", "html"], description="Output formats")
    extract_schema: Optional[Dict[str, Any]] = Field(None, description="Schema for structured data extraction")
    extract_prompt: Optional[str] = Field(None, description="Prompt for extraction without schema")
    proxy: Optional[Literal["basic", "stealth"]] = Field(None, description="Proxy type (basic or stealth)")
    retry_with_stealth: Optional[bool] = Field(True, description="Whether to retry with stealth proxy if basic fails")
    
class JobStatusResponse(SerializableBaseModel):
    job_id: UUID
    status: str
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
class ScrapeResponse(SerializableBaseModel):
    job_id: UUID
    status: str

class CrawlResponse(SerializableBaseModel):
    job_id: UUID
    status: str
    webhook_url: Optional[str] = None

class WebSocketResponse(SerializableBaseModel):
    connection_id: str
    status: str

class BatchScrapeResponse(SerializableBaseModel):
    job_id: UUID
    status: str

class MapRequest(SerializableBaseModel):
    url: str = Field(..., description="URL to map")
    search: Optional[str] = Field(None, description="Optional search term to filter URLs by relevance")
    timeout: Optional[int] = Field(None, description="Timeout in milliseconds")
    limit: Optional[int] = Field(100, description="Maximum number of links to return")
    ignore_sitemap: Optional[bool] = Field(True, description="Ignore the website sitemap when crawling")
    include_subdomains: Optional[bool] = Field(False, description="Include subdomains of the website")

class MapResponse(SerializableBaseModel):
    status: str = Field(..., description="Status of the mapping operation")
    links: List[str] = Field(..., description="List of links found on the website") 