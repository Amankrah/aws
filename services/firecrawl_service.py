from firecrawl import FirecrawlApp
from django.conf import settings
from typing import Dict, List, Any, Optional, Union, Callable
import json
import logging
import uuid

# Set up logging
logger = logging.getLogger(__name__)

def sanitize_json_data(data):
    """Sanitize JSON data to remove non-serializable objects like functions."""
    if isinstance(data, dict):
        return {k: sanitize_json_data(v) for k, v in data.items() if not callable(v)}
    elif isinstance(data, list):
        return [sanitize_json_data(item) for item in data]
    elif callable(data):
        return str(data)
    else:
        return data

class FirecrawlService:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        self.client = FirecrawlApp(api_key=self.api_key)
    
    def map_url(self, url, search=None, timeout=None, limit=100, ignore_sitemap=True, include_subdomains=False):
        """
        Map a website to get all urls on the website extremely fast
        
        Args:
            url (str): The URL to map
            search (str): Optional search term to filter the urls by relevance
            timeout (int): Optional timeout in milliseconds
            limit (int): Maximum number of links to return
            ignore_sitemap (bool): Ignore the website sitemap when crawling
            include_subdomains (bool): Include subdomains of the website
            
        Returns:
            Dict: Map results containing list of links
        """
        try:
            params = {}
            
            if search:
                params["search"] = search
                
            if timeout:
                params["timeout"] = timeout
                
            params["limit"] = limit
            params["ignoreSitemap"] = ignore_sitemap
            params["includeSubdomains"] = include_subdomains
                
            return self.client.map_url(url, **params)
        except Exception as e:
            print(f"Error mapping URL {url}: {str(e)}")
            return {"error": str(e), "links": []}
    
    def scrape_url(self, url, formats=None, actions=None, location=None, json_options=None, change_tracking_options=None, 
                   proxy=None, retry_with_stealth=True, agent=None, only_main_content=True, include_tags=None, exclude_tags=None,
                   wait_for=0, timeout=30000, parse_pdf=True):
        """
        Scrape a single URL and return its content
        
        Args:
            url (str): The URL to scrape
            formats (List[str]): Output formats ("markdown", "html", "screenshot", "json", "links", "changeTracking")
            actions (List[Dict]): Sequence of actions to perform before scraping (click, wait, etc.)
            location (Dict): Location settings (country, languages)
            json_options (Dict): Options for JSON extraction (schema, prompt)
            change_tracking_options (Dict): Options for change tracking
            proxy (str): Proxy type ("basic" or "stealth")
            retry_with_stealth (bool): Whether to retry with stealth proxy if basic fails with specific error codes
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            only_main_content (bool): Whether to return only the main content of the page
            include_tags (List[str]): HTML tags, classes and ids to include
            exclude_tags (List[str]): HTML tags, classes and ids to exclude
            wait_for (int): Time to wait for the page to load in milliseconds
            timeout (int): Maximum time to wait for the page to respond in milliseconds
            parse_pdf (bool): Whether to parse PDF content if the URL points to a PDF
            
        Returns:
            Dict: Scraped content in requested formats
        """
        formats = formats or ["markdown", "html"]
        try:
            params = {
                "formats": formats
            }
            
            if actions:
                params["actions"] = actions
                
            if location:
                params["location"] = location
                
            if json_options and "json" in formats:
                params["json_options"] = json_options
                
            if change_tracking_options and "changeTracking" in formats:
                params["change_tracking_options"] = change_tracking_options
                
            if proxy:
                params["proxy"] = proxy
                
            if agent:
                params["agent"] = agent
                
            # Add advanced scraping options
            params["onlyMainContent"] = only_main_content
            
            if include_tags:
                params["includeTags"] = include_tags
                
            if exclude_tags:
                params["excludeTags"] = exclude_tags
                
            if wait_for > 0:
                params["waitFor"] = wait_for
                
            params["timeout"] = timeout
            params["parsePDF"] = parse_pdf
            
            logger.info(f"Calling scrape_url with params: {params}")
            result = self.client.scrape_url(url, **params)
            logger.info(f"Scrape result type: {type(result).__name__}")
            
            # Sanitize result to remove non-serializable objects like functions
            if isinstance(result, dict):
                result = sanitize_json_data(result)
            
            # Check if the result is not a dictionary and needs conversion
            if not isinstance(result, dict):
                logger.warning(f"ScrapeResponse is not a dictionary, attempting to convert: {type(result).__name__}")
                try:
                    # Try to convert the response to a dictionary
                    if hasattr(result, '__dict__'):
                        logger.info("Converting using __dict__")
                        result = result.__dict__
                    elif hasattr(result, 'to_dict'):
                        logger.info("Converting using to_dict()")
                        result = result.to_dict()
                    elif hasattr(result, 'to_json'):
                        logger.info("Converting using to_json()")
                        result = json.loads(result.to_json())
                    else:
                        # Handle specific known structure of ScrapeResponse
                        logger.info("Creating dictionary from attributes")
                        result = {
                            "metadata": getattr(result, "metadata", {}),
                            "html": getattr(result, "html", ""),
                            "markdown": getattr(result, "markdown", ""),
                            "json": getattr(result, "json", None),
                            "screenshot": getattr(result, "screenshot", None),
                            "links": getattr(result, "links", [])
                        }
                    
                    # Sanitize the converted result
                    result = sanitize_json_data(result)
                    
                except Exception as conversion_error:
                    logger.error(f"Error converting ScrapeResponse to dict: {str(conversion_error)}")
            
            # Check if we need to retry with stealth proxy
            if retry_with_stealth and proxy != "stealth":
                status_code = result.get("metadata", {}).get("statusCode")
                if status_code in [401, 403, 500]:
                    logger.info(f"Got status code {status_code}, retrying with stealth proxy")
                    params["proxy"] = "stealth"
                    retry_result = self.client.scrape_url(url, **params)
                    logger.info(f"Stealth retry result type: {type(retry_result).__name__}")
                    
                    # Convert retry result if needed
                    if not isinstance(retry_result, dict):
                        logger.warning("Stealth retry response is not a dictionary, attempting to convert")
                        try:
                            if hasattr(retry_result, '__dict__'):
                                retry_result = retry_result.__dict__
                            elif hasattr(retry_result, 'to_dict'):
                                retry_result = retry_result.to_dict()
                            elif hasattr(retry_result, 'to_json'):
                                retry_result = json.loads(retry_result.to_json())
                            else:
                                retry_result = {
                                    "metadata": getattr(retry_result, "metadata", {}),
                                    "html": getattr(retry_result, "html", ""),
                                    "markdown": getattr(retry_result, "markdown", ""),
                                    "json": getattr(retry_result, "json", None),
                                    "screenshot": getattr(retry_result, "screenshot", None),
                                    "links": getattr(retry_result, "links", [])
                                }
                                
                            # Sanitize the retry result
                            retry_result = sanitize_json_data(retry_result)
                            
                        except Exception as retry_conversion_error:
                            logger.error(f"Error converting stealth retry response: {str(retry_conversion_error)}")
                    
                    return retry_result
                    
            return result
        except Exception as e:
            # If initial request fails and we should retry with stealth
            if retry_with_stealth and proxy != "stealth":
                try:
                    logger.info(f"Initial scrape failed, retrying with stealth proxy: {str(e)}")
                    params = params if 'params' in locals() else {"formats": formats}
                    params["proxy"] = "stealth"
                    retry_result = self.client.scrape_url(url, **params)
                    logger.info(f"Stealth fallback result type: {type(retry_result).__name__}")
                    
                    # Convert retry result if needed
                    if not isinstance(retry_result, dict):
                        logger.warning("Stealth fallback response is not a dictionary, attempting to convert")
                        try:
                            if hasattr(retry_result, '__dict__'):
                                retry_result = retry_result.__dict__
                            elif hasattr(retry_result, 'to_dict'):
                                retry_result = retry_result.to_dict()
                            elif hasattr(retry_result, 'to_json'):
                                retry_result = json.loads(retry_result.to_json())
                            else:
                                retry_result = {
                                    "metadata": getattr(retry_result, "metadata", {}),
                                    "html": getattr(retry_result, "html", ""),
                                    "markdown": getattr(retry_result, "markdown", ""),
                                    "json": getattr(retry_result, "json", None),
                                    "screenshot": getattr(retry_result, "screenshot", None),
                                    "links": getattr(retry_result, "links", [])
                                }
                                
                            # Sanitize the retry result
                            retry_result = sanitize_json_data(retry_result)
                            
                        except Exception as fallback_conversion_error:
                            logger.error(f"Error converting stealth fallback response: {str(fallback_conversion_error)}")
                    
                    return retry_result
                except Exception as stealth_error:
                    logger.error(f"Stealth proxy also failed: {str(stealth_error)}")
                    return {"error": f"Both basic and stealth proxies failed. Basic: {str(e)}, Stealth: {str(stealth_error)}"}
            
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {"error": str(e)}
    
    def crawl_url(self, url, limit=10, scrape_options=None, proxy=None, allow_backward_links=False, 
                  include_paths=None, exclude_paths=None, allowed_domains=None, webhook=None, poll_interval=15, agent=None,
                  max_depth=None, allow_external_links=False, delay=None):
        """
        Crawl a domain starting from a URL
        
        Args:
            url (str): The URL to start crawling from
            limit (int): Maximum number of pages to crawl
            scrape_options (Dict): Options for scraping pages
            proxy (str): Proxy type ("basic" or "stealth")
            allow_backward_links (bool): Whether to follow links outside the direct children of starting URL
            include_paths (List[str]): Glob patterns for paths to include
            exclude_paths (List[str]): Glob patterns for paths to exclude
            allowed_domains (List[str]): List of domains allowed to crawl
            webhook (str): Webhook URL to receive crawl events
            poll_interval (int): Interval in seconds to poll for crawl status
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            max_depth (int): Maximum depth to crawl relative to the entered URL
            allow_external_links (bool): Whether to follow links that point to external domains
            delay (int): Delay in seconds between scrapes
        """
        scrape_options = scrape_options or {"formats": ["markdown", "html"]}
        
        # Add proxy to scrape options if specified
        if proxy:
            scrape_options["proxy"] = proxy
            
        # Add agent to scrape options if specified
        if agent:
            scrape_options["agent"] = agent
            
        try:
            # Build crawl parameters
            params = {
                "limit": limit,
                "scrapeOptions": scrape_options
            }
            
            if allow_backward_links:
                params["allowBackwardLinks"] = True
                
            if include_paths:
                params["includePaths"] = include_paths
                
            if exclude_paths:
                params["excludePaths"] = exclude_paths
                
            if allowed_domains:
                params["allowedDomains"] = allowed_domains
                
            if webhook:
                params["webhook"] = webhook
                
            # Add advanced crawling options
            if max_depth is not None:
                params["maxDepth"] = max_depth
                
            if allow_external_links:
                params["allowExternalLinks"] = True
                
            if delay is not None:
                params["delay"] = delay
                
            return self.client.crawl_url(url, poll_interval=poll_interval, **params)
        except Exception as e:
            print(f"Error crawling URL {url}: {str(e)}")
            return {"error": str(e)}
    
    def async_crawl_url(self, url, limit=10, scrape_options=None, proxy=None, allow_backward_links=False, 
                        include_paths=None, exclude_paths=None, allowed_domains=None, webhook=None, agent=None,
                        max_depth=None, allow_external_links=False, delay=None):
        """
        Start an asynchronous crawl job and return a job ID
        
        Args:
            url (str): The URL to start crawling from
            limit (int): Maximum number of pages to crawl
            scrape_options (Dict): Options for scraping pages
            proxy (str): Proxy type ("basic" or "stealth")
            allow_backward_links (bool): Whether to follow links outside the direct children of starting URL
            include_paths (List[str]): Glob patterns for paths to include
            exclude_paths (List[str]): Glob patterns for paths to exclude
            allowed_domains (List[str]): List of domains allowed to crawl
            webhook (str): Webhook URL to receive crawl events
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            max_depth (int): Maximum depth to crawl relative to the entered URL
            allow_external_links (bool): Whether to follow links that point to external domains
            delay (int): Delay in seconds between scrapes
            
        Returns:
            Dict: Job ID and URL for checking status
        """
        scrape_options = scrape_options or {"formats": ["markdown", "html"]}
        
        # Add proxy to scrape options if specified
        if proxy:
            scrape_options["proxy"] = proxy
            
        # Add agent to scrape options if specified
        if agent:
            scrape_options["agent"] = agent
            
        try:
            # Build crawl parameters
            params = {
                "limit": limit,
                "scrapeOptions": scrape_options
            }
            
            if allow_backward_links:
                params["allowBackwardLinks"] = True
                
            if include_paths:
                params["includePaths"] = include_paths
                
            if exclude_paths:
                params["excludePaths"] = exclude_paths
                
            if allowed_domains:
                params["allowedDomains"] = allowed_domains
                
            if webhook:
                params["webhook"] = webhook
                
            # Add advanced crawling options
            if max_depth is not None:
                params["maxDepth"] = max_depth
                
            if allow_external_links:
                params["allowExternalLinks"] = True
                
            if delay is not None:
                params["delay"] = delay
                
            return self.client.async_crawl_url(url, **params)
        except Exception as e:
            print(f"Error starting async crawl for URL {url}: {str(e)}")
            return {"error": str(e)}
    
    def crawl_url_and_watch(self, url, limit=10, scrape_options=None, proxy=None, allow_backward_links=False,
                           include_paths=None, exclude_paths=None, allowed_domains=None,
                           on_document=None, on_error=None, on_done=None, agent=None,
                           max_depth=None, allow_external_links=False, delay=None):
        """
        Start a websocket-based crawl that provides real-time updates
        
        Args:
            url (str): The URL to start crawling from
            limit (int): Maximum number of pages to crawl
            scrape_options (Dict): Options for scraping pages
            proxy (str): Proxy type ("basic" or "stealth")
            allow_backward_links (bool): Whether to follow links outside the direct children of starting URL
            include_paths (List[str]): Glob patterns for paths to include
            exclude_paths (List[str]): Glob patterns for paths to exclude
            allowed_domains (List[str]): List of domains allowed to crawl
            on_document (Callable): Callback for document events
            on_error (Callable): Callback for error events
            on_done (Callable): Callback for completion events
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            max_depth (int): Maximum depth to crawl relative to the entered URL
            allow_external_links (bool): Whether to follow links that point to external domains
            delay (int): Delay in seconds between scrapes
            
        Returns:
            Object: Watcher object with event listeners
        """
        scrape_options = scrape_options or {"formats": ["markdown", "html"]}
        
        # Add proxy to scrape options if specified
        if proxy:
            scrape_options["proxy"] = proxy
            
        # Add agent to scrape options if specified
        if agent:
            scrape_options["agent"] = agent
            
        try:
            # Build crawl parameters
            params = {
                "limit": limit,
                "scrapeOptions": scrape_options
            }
            
            if allow_backward_links:
                params["allowBackwardLinks"] = True
                
            if include_paths:
                params["includePaths"] = include_paths
                
            if exclude_paths:
                params["excludePaths"] = exclude_paths
                
            if allowed_domains:
                params["allowedDomains"] = allowed_domains
            
            # Add advanced crawling options
            if max_depth is not None:
                params["maxDepth"] = max_depth
                
            if allow_external_links:
                params["allowExternalLinks"] = True
                
            if delay is not None:
                params["delay"] = delay
                
            # Get the watcher object
            watcher = self.client.crawl_url_and_watch(url, **params)
            
            # Add event listeners if provided
            if on_document:
                watcher.add_event_listener("document", on_document)
                
            if on_error:
                watcher.add_event_listener("error", on_error)
                
            if on_done:
                watcher.add_event_listener("done", on_done)
                
            return watcher
        except Exception as e:
            print(f"Error setting up crawl watcher for URL {url}: {str(e)}")
            return {"error": str(e)}
    
    def search(self, query, limit=5, scrape_options=None, lang=None, country=None, tbs=None, timeout=None):
        """
        Search the web and return results
        
        Args:
            query (str): The search query
            limit (int): Maximum number of results to return
            scrape_options (Dict): Options for scraping search results, including formats
            lang (str): Language code (e.g., 'en', 'de', 'fr')
            country (str): Country code (e.g., 'us', 'de', 'fr')
            tbs (str): Time-based search parameter (e.g., 'qdr:h' for past hour, 'qdr:d' for past day)
            timeout (int): Timeout in milliseconds
            
        Returns:
            Dict: Search results, optionally with scraped content
        """
        try:
            params = {
                "limit": limit
            }
            
            if scrape_options:
                params["scrape_options"] = scrape_options
                
            if lang:
                params["lang"] = lang
                
            if country:
                params["country"] = country
                
            if tbs:
                params["tbs"] = tbs
                
            if timeout:
                params["timeout"] = timeout
                
            # Get the search response from the client
            search_response = self.client.search(query, **params)
            
            # Sanitize result to remove non-serializable objects like functions
            if isinstance(search_response, dict):
                search_response = sanitize_json_data(search_response)
            
            # Convert SearchResponse object to a dictionary if it's not already
            if not isinstance(search_response, dict):
                try:
                    # Try to convert the response to a dictionary
                    if hasattr(search_response, '__dict__'):
                        search_response = search_response.__dict__
                    elif hasattr(search_response, 'to_dict'):
                        search_response = search_response.to_dict()
                    elif hasattr(search_response, 'to_json'):
                        search_response = json.loads(search_response.to_json())
                    else:
                        # Handle specific known structure of SearchResponse
                        search_response = {
                            "data": getattr(search_response, "data", []),
                            "metadata": getattr(search_response, "metadata", {})
                        }
                        
                    # Sanitize the converted result
                    search_response = sanitize_json_data(search_response)
                    
                except Exception as conversion_error:
                    logger.error(f"Error converting SearchResponse to dict: {str(conversion_error)}")
                    return {"error": f"Error converting search response: {str(conversion_error)}"}
            
            return search_response
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return {"error": str(e)}
    
    def extract_structured_data(self, url, schema=None, prompt=None, proxy=None, retry_with_stealth=True, agent=None):
        """
        Extract structured data according to a schema or prompt
        
        Args:
            url (str): The URL to extract data from
            schema (Dict): JSON schema for extraction
            prompt (str): Prompt for extraction without schema
            proxy (str): Proxy type ("basic" or "stealth")
            retry_with_stealth (bool): Whether to retry with stealth proxy if basic fails
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Extracted structured data
        """
        try:
            json_options = {}
            
            if schema:
                json_options["schema"] = schema
            elif prompt:
                json_options["prompt"] = prompt
            
            params = {
                "formats": ["json"],
                "json_options": json_options
            }
            
            if proxy:
                params["proxy"] = proxy
                
            if agent:
                params["agent"] = agent
                
            result = self.client.scrape_url(url, **params)
            
            # Check if we need to retry with stealth proxy
            if retry_with_stealth and proxy != "stealth":
                status_code = result.get("metadata", {}).get("statusCode")
                if status_code in [401, 403, 500]:
                    print(f"Got status code {status_code}, retrying extraction with stealth proxy")
                    params["proxy"] = "stealth"
                    return self.client.scrape_url(url, **params)
                    
            return result
            
        except Exception as e:
            # If initial request fails and we should retry with stealth
            if retry_with_stealth and proxy != "stealth":
                try:
                    print(f"Initial extraction failed, retrying with stealth proxy: {str(e)}")
                    params = params if 'params' in locals() else {
                        "formats": ["json"],
                        "json_options": json_options
                    }
                    params["proxy"] = "stealth"
                    return self.client.scrape_url(url, **params)
                except Exception as stealth_error:
                    print(f"Stealth proxy also failed: {str(stealth_error)}")
                    return {"error": f"Both basic and stealth proxies failed. Basic: {str(e)}, Stealth: {str(stealth_error)}"}
                    
            print(f"Error extracting structured data from {url}: {str(e)}")
            return {"error": str(e)}
    
    def batch_scrape_urls(self, urls, formats=None, json_options=None, proxy=None, agent=None):
        """
        Batch scrape multiple URLs
        
        Args:
            urls (List[str]): List of URLs to scrape
            formats (List[str]): Output formats
            json_options (Dict): Options for JSON extraction
            proxy (str): Proxy type ("basic" or "stealth")
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Results of batch scrape job
        """
        formats = formats or ["markdown", "html"]
        try:
            params = {
                "formats": formats
            }
            
            if json_options and "json" in formats:
                params["json_options"] = json_options
                
            if proxy:
                params["proxy"] = proxy
                
            if agent:
                params["agent"] = agent
            
            logger.info(f"Calling batch_scrape_urls with params: {params}")
            result = self.client.batch_scrape_urls(urls, **params)
            logger.info(f"Batch scrape result type: {type(result).__name__}")
            
            # Sanitize result to remove non-serializable objects like functions
            if isinstance(result, dict):
                result = sanitize_json_data(result)
            
            # Check if the result is not a dictionary and needs conversion
            if not isinstance(result, dict):
                logger.warning(f"BatchScrapeResponse is not a dictionary, attempting to convert: {type(result).__name__}")
                try:
                    # Try to convert the response to a dictionary
                    if hasattr(result, '__dict__'):
                        logger.info("Converting using __dict__")
                        result = result.__dict__
                    elif hasattr(result, 'to_dict'):
                        logger.info("Converting using to_dict()")
                        result = result.to_dict()
                    elif hasattr(result, 'to_json'):
                        logger.info("Converting using to_json()")
                        result = json.loads(result.to_json())
                    else:
                        # Handle specific known structure
                        logger.info("Creating dictionary from attributes")
                        result = {
                            "id": getattr(result, "id", str(uuid.uuid4())),
                            "status": getattr(result, "status", "pending"),
                            "data": getattr(result, "data", [])
                        }
                        
                    # Sanitize the converted result
                    result = sanitize_json_data(result)
                    
                except Exception as conversion_error:
                    logger.error(f"Error converting BatchScrapeResponse to dict: {str(conversion_error)}")
                    return {"error": f"Error converting batch scrape response: {str(conversion_error)}"}
            
            return result
        except Exception as e:
            logger.error(f"Error batch scraping URLs: {str(e)}")
            return {"error": str(e)}
    
    def async_batch_scrape_urls(self, urls, formats=None, json_options=None, proxy=None, agent=None):
        """
        Asynchronously batch scrape multiple URLs and return a job ID
        
        Args:
            urls (List[str]): List of URLs to scrape
            formats (List[str]): Output formats
            json_options (Dict): Options for JSON extraction
            proxy (str): Proxy type ("basic" or "stealth")
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Job ID for the batch scrape
        """
        formats = formats or ["markdown", "html"]
        try:
            params = {
                "formats": formats
            }
            
            if json_options and "json" in formats:
                params["json_options"] = json_options
                
            if proxy:
                params["proxy"] = proxy
                
            if agent:
                params["agent"] = agent
                
            return self.client.async_batch_scrape_urls(urls, **params)
        except Exception as e:
            print(f"Error starting async batch scrape: {str(e)}")
            return {"error": str(e)}
    
    def check_batch_scrape_status(self, job_id):
        """
        Check the status of a batch scrape job
        
        Args:
            job_id (str): The ID of the batch scrape job
            
        Returns:
            Dict: Status of the batch scrape job
        """
        try:
            return self.client.check_batch_scrape_status(job_id)
        except Exception as e:
            print(f"Error checking batch scrape status: {str(e)}")
            return {"error": str(e)}
            
    def check_crawl_status(self, job_id):
        """
        Check the status of a crawl job
        
        Args:
            job_id (str): The ID of the crawl job
            
        Returns:
            Dict: Status of the crawl job
        """
        try:
            return self.client.check_crawl_status(job_id)
        except Exception as e:
            print(f"Error checking crawl status: {str(e)}")
            return {"error": str(e)} 