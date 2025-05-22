import uuid
from datetime import datetime
from celery import shared_task
from django.contrib.auth import get_user_model
import logging
import json

from apps.crawl_jobs.models import CrawlJob, CrawlResult
from services.firecrawl_service import FirecrawlService, sanitize_json_data
from services.claude_service import ClaudeService
from services.scratchpad_service import ScratchpadService

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

# Helper function to safely serialize content for storage
def safe_serialize(content):
    """
    Ensure content is safely serializable by sanitizing and converting to JSON if needed
    """
    # If it's already a string, return it
    if isinstance(content, str):
        return content
        
    # First sanitize to remove callable objects
    sanitized = sanitize_json_data(content)
    
    # Try to serialize to JSON string
    try:
        return json.dumps(sanitized)
    except TypeError as e:
        logger.error(f"Type error serializing content: {str(e)}")
        # Fall back to string representation
        return str(sanitized)
    except Exception as e:
        logger.error(f"Error serializing content: {str(e)}")
        return str(sanitized)

@shared_task
def start_crawl_job(job_id, user_id):
    """
    Start a crawl job as a background task
    """
    logger.info(f"Starting crawl job: {job_id} for user: {user_id}")
    try:
        job = CrawlJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.save()
        
        # Get user and their API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        firecrawl_service = FirecrawlService(api_key=firecrawl_api_key)
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Check for advanced options
        options = job.options or {}
        logger.info(f"Job options: {options}")
        
        formats = options.get("formats", ["markdown", "html"])
        actions = options.get("actions", None)
        location = options.get("location", None)
        proxy = options.get("proxy", None)
        retry_with_stealth = options.get("retry_with_stealth", True)
        
        # Advanced scraping options
        only_main_content = options.get("only_main_content", True)
        include_tags = options.get("include_tags", None)
        exclude_tags = options.get("exclude_tags", None)
        wait_for = options.get("wait_for", 0)
        timeout = options.get("timeout", 30000)
        parse_pdf = options.get("parse_pdf", True)
        
        # Extract AI agent configuration if provided
        agent = None
        if options.get("agent"):
            agent = options.get("agent")
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')}")
        
        # Extract schema/prompt if provided
        json_options = None
        if options.get("extract_schema") or options.get("extract_prompt"):
            json_options = {}
            if "extract_schema" in options:
                json_options["schema"] = options["extract_schema"]
            if "extract_prompt" in options:
                json_options["prompt"] = options["extract_prompt"]
            
            # Add json format if we're doing extraction
            if "json" not in formats:
                formats.append("json")
        
        # Extract crawl-specific options
        max_depth = options.get("max_depth", None)
        allow_backward_links = options.get("allow_backward_links", False)
        allow_external_links = options.get("allow_external_links", False)
        delay = options.get("delay", None)
        include_paths = options.get("include_paths", None)
        exclude_paths = options.get("exclude_paths", None)
        
        # Initialize scratchpad with the query
        scratchpad_service.save("initial_query", job.query)
        
        # Generate scraping plan with Claude
        planning_prompt = f"""
        I need to extract information about: {job.query}
        
        If we should look in a specific company domain first: {job.domain if job.domain else 'None provided'}
        
        Create a detailed plan for how to extract this information using web scraping.
        Include which URLs to start with, what data to extract, and how to process it.
        """
        
        planning_response = claude_service.generate_response(planning_prompt)
        scratchpad_service.save("scraping_plan", planning_response)
        
        # Log proxy usage
        if proxy:
            scratchpad_service.save("proxy_type", f"Using {proxy} proxy type")
        
        # Execute the plan using Firecrawl
        if job.domain:
            logger.info(f"Crawling domain: {job.domain}")
            try:
                # Prepare crawl options
                scrape_options = {
                    "formats": formats,
                    "actions": actions,
                    "location": location,
                    "json_options": json_options,
                    "agent": agent,
                    "onlyMainContent": only_main_content,
                    "includeTags": include_tags,
                    "excludeTags": exclude_tags,
                    "waitFor": wait_for,
                    "timeout": timeout,
                    "parsePDF": parse_pdf
                }
                
                logger.info(f"Crawl options: {scrape_options}")
                
                # Try company domain first
                domain_result = firecrawl_service.crawl_url(
                    job.domain, 
                    limit=10,
                    scrape_options=scrape_options,
                    proxy=proxy,
                    allow_backward_links=allow_backward_links,
                    include_paths=include_paths,
                    exclude_paths=exclude_paths,
                    max_depth=max_depth,
                    allow_external_links=allow_external_links,
                    delay=delay
                )
                
                # Log domain result type
                logger.info(f"Domain result type: {type(domain_result).__name__}")
                
                # Check if result is JSON serializable
                try:
                    json.dumps(domain_result)
                    logger.info("Domain result is JSON serializable")
                except TypeError as e:
                    logger.error(f"Domain result is not JSON serializable: {str(e)}")
                    # Attempt to convert non-serializable object to dict
                    if not isinstance(domain_result, dict):
                        logger.warning("Converting domain_result to dictionary")
                        if hasattr(domain_result, '__dict__'):
                            domain_result = domain_result.__dict__
                        elif hasattr(domain_result, 'to_dict'):
                            domain_result = domain_result.to_dict()
                
                scratchpad_service.save("domain_results", domain_result, content_type="json")
                
                # Store results in database
                result_count = 0
                for item in domain_result.get('data', []):
                    try:
                        CrawlResult.objects.create(
                            crawl_job=job,
                            url=item.get('metadata', {}).get('sourceURL', ''),
                            title=item.get('metadata', {}).get('title', ''),
                            content=safe_serialize(item.get('markdown', '')),
                            content_type='markdown',
                            metadata=sanitize_json_data(item.get('metadata', {}))
                        )
                        result_count += 1
                        
                        # If JSON data is available, store that too
                        if "json" in item:
                            CrawlResult.objects.create(
                                crawl_job=job,
                                url=item.get('metadata', {}).get('sourceURL', ''),
                                title=f"Structured data for {item.get('metadata', {}).get('title', '')}",
                                content=safe_serialize(item.get('json', {})),
                                content_type='json',
                                metadata={"type": "extraction"}
                            )
                            result_count += 1
                    except Exception as item_error:
                        logger.error(f"Error storing domain result item: {str(item_error)}")
                
                logger.info(f"Stored {result_count} results from domain crawl")
            except Exception as domain_error:
                logger.error(f"Domain crawl error: {str(domain_error)}")
                scratchpad_service.save("domain_error", str(domain_error))
                domain_result = None
        
        # If domain search fails or isn't specified, use internet search
        if not job.domain or not domain_result or not domain_result.get('data'):
            logger.info(f"Performing search for: {job.query}")
            search_results = firecrawl_service.search(job.query, limit=5)
            
            # Log search result type
            logger.info(f"Search result type: {type(search_results).__name__}")
            
            # Check if search result is JSON serializable
            try:
                json.dumps(search_results)
                logger.info("Search result is JSON serializable")
            except TypeError as e:
                logger.error(f"Search result is not JSON serializable: {str(e)}")
                # Attempt to convert non-serializable object to dict
                if not isinstance(search_results, dict):
                    logger.warning("Converting search_results to dictionary")
                    if hasattr(search_results, '__dict__'):
                        search_results = search_results.__dict__
                    elif hasattr(search_results, 'to_dict'):
                        search_results = search_results.to_dict()
            
            scratchpad_service.save("search_results", search_results, content_type="json")
            
            # Extract full content from top search results
            result_count = 0
            for i, result in enumerate(search_results.get('data', [])[:3]):
                url = result.get("url")
                logger.info(f"Scraping URL from search results: {url}")
                
                content = firecrawl_service.scrape_url(
                    url, 
                    formats=formats,
                    actions=actions,
                    location=location,
                    json_options=json_options,
                    proxy=proxy,
                    retry_with_stealth=retry_with_stealth,
                    agent=agent,
                    only_main_content=only_main_content,
                    include_tags=include_tags,
                    exclude_tags=exclude_tags,
                    wait_for=wait_for,
                    timeout=timeout,
                    parse_pdf=parse_pdf
                )
                
                # Log content result type
                logger.info(f"Content result type for {url}: {type(content).__name__}")
                
                # Check if content is JSON serializable
                try:
                    json.dumps(content)
                    logger.info(f"Content for {url} is JSON serializable")
                except TypeError as e:
                    logger.error(f"Content for {url} is not JSON serializable: {str(e)}")
                    # Attempt to convert non-serializable object to dict
                    if not isinstance(content, dict):
                        logger.warning(f"Converting content for {url} to dictionary")
                        if hasattr(content, '__dict__'):
                            content = content.__dict__
                        elif hasattr(content, 'to_dict'):
                            content = content.to_dict()
                
                scratchpad_service.save(f"search_content_{i}", content, content_type="json")
                
                try:
                    # Store results in database
                    CrawlResult.objects.create(
                        crawl_job=job,
                        url=url,
                        title=result.get('title', ''),
                        content=safe_serialize(content.get('markdown', '')),
                        content_type='markdown',
                        metadata=sanitize_json_data(content.get('metadata', {}))
                    )
                    result_count += 1
                    
                    # If JSON data is available, store that too
                    if "json" in content:
                        CrawlResult.objects.create(
                            crawl_job=job,
                            url=url,
                            title=f"Structured data for {result.get('title', '')}",
                            content=safe_serialize(content.get('json', {})),
                            content_type='json',
                            metadata={"type": "extraction"}
                        )
                        result_count += 1
                except Exception as item_error:
                    logger.error(f"Error storing search result item: {str(item_error)}")
            
            logger.info(f"Stored {result_count} results from search")
        
        # Generate final synthesis with Claude
        synthesis_prompt = f"""
        Original query: {job.query}
        
        Here is the information we've gathered:
        """
        
        # Add all scratchpad data to the prompt
        keys = scratchpad_service.list_keys()
        for key in keys:
            if key.startswith("domain_results") or key.startswith("search_content"):
                content = scratchpad_service.fetch(key)
                synthesis_prompt += f"\n\n--- {key} ---\n{content}"
        
        synthesis_prompt += "\n\nBased on this information, provide a comprehensive answer to the original query."
        
        final_response = claude_service.generate_response(synthesis_prompt)
        scratchpad_service.save("final_synthesis", final_response)
        
        # Create a final result with the synthesis
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title="Final Synthesis",
            content=safe_serialize(final_response),
            content_type='markdown',
            metadata={"type": "synthesis"}
        )
        
        # Update job status
        job.status = 'completed'
        job.completed_at = datetime.now()
        job.save()
        
    except Exception as e:
        # Update job with error
        job.status = 'failed'
        job.error_message = str(e)
        job.save()

@shared_task
def start_batch_scrape_job(job_id, user_id):
    """
    Start a batch scrape job for multiple URLs
    """
    logger.info(f"Starting batch scrape job: {job_id} for user: {user_id}")
    try:
        job = CrawlJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.save()
        
        # Get user and their API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        firecrawl_service = FirecrawlService(api_key=firecrawl_api_key)
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get batch options
        options = job.options or {}
        logger.info(f"Batch job options: {options}")
        
        urls = options.get("urls", [])
        formats = options.get("formats", ["markdown", "html"])
        proxy = options.get("proxy", None)
        retry_with_stealth = options.get("retry_with_stealth", True)
        
        # Extract AI agent configuration if provided
        agent = None
        if options.get("agent"):
            agent = options.get("agent")
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')} for batch scraping")
        
        # Log proxy usage
        if proxy:
            scratchpad_service.save("proxy_type", f"Using {proxy} proxy type for batch scraping")
        
        # Prepare JSON options if extraction is requested
        json_options = None
        if options.get("extract_schema") or options.get("extract_prompt"):
            json_options = {}
            if "extract_schema" in options:
                json_options["schema"] = options["extract_schema"]
            if "extract_prompt" in options:
                json_options["prompt"] = options["extract_prompt"]
        
        # Initialize scratchpad with the URLs
        scratchpad_service.save("batch_urls", urls, content_type="json")
        logger.info(f"Starting batch scrape for {len(urls)} URLs")
        
        # Start batch scrape
        batch_result = firecrawl_service.batch_scrape_urls(
            urls=urls,
            formats=formats,
            json_options=json_options,
            proxy=proxy,
            agent=agent
        )
        
        # Log batch result type
        logger.info(f"Batch result type: {type(batch_result).__name__}")
        
        # Check if result is JSON serializable
        try:
            json.dumps(batch_result)
            logger.info("Batch result is JSON serializable")
        except TypeError as e:
            logger.error(f"Batch result is not JSON serializable: {str(e)}")
            # Attempt to convert non-serializable object to dict
            if not isinstance(batch_result, dict):
                logger.warning("Converting batch_result to dictionary")
                if hasattr(batch_result, '__dict__'):
                    batch_result = batch_result.__dict__
                elif hasattr(batch_result, 'to_dict'):
                    batch_result = batch_result.to_dict()
                elif hasattr(batch_result, 'to_json'):
                    batch_result = json.loads(batch_result.to_json())
        
        # Store firecrawl job ID if available
        if "id" in batch_result:
            job.firecrawl_job_id = batch_result["id"]
            job.save()
            
        # Save batch results to scratchpad
        scratchpad_service.save("batch_results", batch_result, content_type="json")
        
        # Process results if available immediately
        if "data" in batch_result:
            logger.info(f"Processing {len(batch_result['data'])} immediate batch results")
            # Store each result in the database
            result_count = 0
            for i, item in enumerate(batch_result.get("data", [])):
                url = urls[i] if i < len(urls) else f"url_{i}"
                logger.debug(f"Processing batch result for URL: {url}")
                
                try:
                    # Store markdown content if available
                    if "markdown" in item:
                        CrawlResult.objects.create(
                            crawl_job=job,
                            url=url,
                            title=item.get("metadata", {}).get("title", f"Result {i+1}"),
                            content=safe_serialize(item.get("markdown", "")),
                            content_type="markdown",
                            metadata=sanitize_json_data(item.get("metadata", {}))
                        )
                        result_count += 1
                    
                    # Store HTML content if available
                    if "html" in item:
                        CrawlResult.objects.create(
                            crawl_job=job,
                            url=url,
                            title=f"HTML for {item.get('metadata', {}).get('title', f'Result {i+1}')}",
                            content=safe_serialize(item.get("html", "")[:100000]),  # Limit size
                            content_type="html",
                            metadata=sanitize_json_data(item.get("metadata", {}))
                        )
                        result_count += 1
                    
                    # Store JSON content if available
                    if "json" in item:
                        CrawlResult.objects.create(
                            crawl_job=job,
                            url=url,
                            title=f"Structured data for {item.get('metadata', {}).get('title', f'Result {i+1}')}",
                            content=safe_serialize(item.get('json', {})),
                            content_type="json",
                            metadata={"type": "extraction"}
                        )
                        result_count += 1
                except Exception as item_error:
                    logger.error(f"Error storing batch result item {i}: {str(item_error)}")
            
            logger.info(f"Stored {result_count} results from batch scrape")
        
        # For async jobs, poll until complete
        if "id" in batch_result and not "data" in batch_result:
            # This would typically call a separate task to poll the status
            # but for simplicity, we'll just mark it completed and note that polling is needed
            job.status = "completed"
            job.error_message = "Async batch job started. Results will be available via the Firecrawl API."
            job.completed_at = datetime.now()
            job.save()
            return
        
        # Update job status
        job.status = "completed"
        job.completed_at = datetime.now()
        job.save()
        
    except Exception as e:
        # Update job with error
        job.status = "failed"
        job.error_message = str(e)
        job.save()

@shared_task
def map_website(job_id, user_id):
    """
    Map a website to get all URLs
    """
    try:
        job = CrawlJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.save()
        
        # Get user and their API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        firecrawl_service = FirecrawlService(api_key=firecrawl_api_key)
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get map options
        options = job.options or {}
        search = options.get("search", None)
        timeout = options.get("timeout", None)
        limit = options.get("limit", 100)
        ignore_sitemap = options.get("ignore_sitemap", True)
        include_subdomains = options.get("include_subdomains", False)
        
        # Extract AI agent configuration if provided
        agent = None
        if options.get("agent"):
            agent = options.get("agent")
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')} for website mapping")
        
        # Initialize scratchpad with the query
        scratchpad_service.save("mapping_url", job.query)
        if search:
            scratchpad_service.save("search_filter", search)
        
        # Execute the map operation
        map_result = firecrawl_service.map_url(
            url=job.query,  # Use query field to store the URL to map
            search=search,
            timeout=timeout,
            limit=limit,
            ignore_sitemap=ignore_sitemap,
            include_subdomains=include_subdomains
        )
        
        # Save map results to scratchpad
        scratchpad_service.save("map_results", map_result, content_type="json")
        
        # Store results in database
        if "links" in map_result:
            # Create a combined result with all links
            combined_links = "\n".join(map_result["links"])
            CrawlResult.objects.create(
                crawl_job=job,
                url=job.query,
                title="Website Map Results",
                content=safe_serialize(combined_links),
                content_type="text",
                metadata={"type": "map", "link_count": len(map_result["links"])}
            )
            
            # Store individual links
            for i, link in enumerate(map_result["links"]):
                CrawlResult.objects.create(
                    crawl_job=job,
                    url=link,
                    title=f"Link {i+1}",
                    content=link,
                    content_type="url",
                    metadata={"type": "map_link", "index": i}
                )
        
        # Update job status
        job.status = 'completed'
        job.completed_at = datetime.now()
        job.save()
        
    except Exception as e:
        # Update job with error
        job.status = 'failed'
        job.error_message = str(e)
        job.save() 