from celery import shared_task
from datetime import datetime
import json
import uuid
from django.contrib.auth import get_user_model

from apps.crawl_jobs.models import CrawlJob, CrawlResult
from services.extraction_service import ExtractionService
from services.scratchpad_service import ScratchpadService

User = get_user_model()

@shared_task
def extract_structured_data(job_id, user_id, schema, content_key="final_synthesis"):
    """
    Extract structured data from content using a specified schema
    """
    try:
        # Get user and API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        extraction_service = ExtractionService(firecrawl_service_api_key=firecrawl_api_key, user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Get options
        options = job.options or {}
        
        # Extract AI agent configuration if provided
        agent = None
        if options.get("agent"):
            agent = options.get("agent")
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')} for structured data extraction")
        
        # Get content from scratchpad
        content = scratchpad_service.fetch(content_key)
        if not content:
            # If the specific key doesn't exist, try to get content from job results
            try:
                synthesis_result = CrawlResult.objects.get(
                    crawl_job_id=job.id,
                    title="Final Synthesis"
                )
                content = synthesis_result.content
            except CrawlResult.DoesNotExist:
                job.error_message = f"No content found with key '{content_key}'"
                job.save()
                return
        
        # Extract structured data
        structured_data = extraction_service.extract_structured_data(content, schema)
        
        # Save to scratchpad
        scratchpad_service.save(
            f"structured_data_{job_id}", 
            structured_data, 
            content_type="json"
        )
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title="Structured Data Extraction",
            content=json.dumps(structured_data, indent=2),
            content_type="json",
            metadata={"type": "structured_data", "schema": schema}
        )
        
        return structured_data
        
    except Exception as e:
        # Log error
        print(f"Error in extract_structured_data task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Extraction error: {str(e)}"
            job.save()
        return None

@shared_task
def analyze_multiple_urls(job_id, user_id, urls=None, analysis_type="sentiment"):
    """
    Analyze content from multiple URLs
    """
    try:
        # Get user and API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        extraction_service = ExtractionService(firecrawl_service_api_key=firecrawl_api_key, user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # If no URLs provided, get from job results
        if not urls:
            results = CrawlResult.objects.filter(crawl_job_id=job.id)
            urls = [result.url for result in results if result.url]
        
        # Process each URL
        analysis_results = {}
        for url in urls:
            if not url:
                continue
                
            # Get content
            content_result = None
            try:
                content_result = CrawlResult.objects.get(
                    crawl_job_id=job.id,
                    url=url
                )
            except CrawlResult.DoesNotExist:
                # Skip if no content
                continue
                
            content = content_result.content
            
            # Perform the requested analysis
            if analysis_type == "sentiment":
                result = extraction_service.analyze_sentiment(content)
            else:
                result = {"error": f"Unknown analysis type: {analysis_type}"}
                
            # Store result
            analysis_results[url] = result
        
        # Save combined results
        scratchpad_service.save(
            f"{analysis_type}_analysis_{job_id}", 
            analysis_results, 
            content_type="json"
        )
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title=f"{analysis_type.capitalize()} Analysis",
            content=json.dumps(analysis_results, indent=2),
            content_type="json",
            metadata={"type": analysis_type + "_analysis"}
        )
        
        return analysis_results
        
    except Exception as e:
        # Log error
        print(f"Error in analyze_multiple_urls task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Analysis error: {str(e)}"
            job.save()
        return None

@shared_task
def extract_specific_elements_from_urls(job_id, user_id, selectors, urls=None):
    """
    Extract specific elements from multiple URLs using CSS selectors
    """
    try:
        # Get user and API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        extraction_service = ExtractionService(firecrawl_service_api_key=firecrawl_api_key, user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Get options
        options = job.options or {}
        
        # Get agent configuration
        agent = options.get("agent", None)
        if agent:
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')} for element extraction")
        
        # If no URLs provided, get from job results
        if not urls:
            results = CrawlResult.objects.filter(crawl_job_id=job.id)
            urls = [result.url for result in results if result.url]
        
        # Process each URL
        extraction_results = {}
        for url in urls:
            if not url:
                continue
                
            # Extract elements
            result = extraction_service.extract_specific_elements(url, selectors, agent=agent)
            extraction_results[url] = result
        
        # Save combined results
        scratchpad_service.save(
            f"element_extraction_{job_id}", 
            extraction_results, 
            content_type="json"
        )
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title="Element Extraction",
            content=json.dumps(extraction_results, indent=2),
            content_type="json",
            metadata={"type": "element_extraction", "selectors": selectors}
        )
        
        return extraction_results
        
    except Exception as e:
        # Log error
        print(f"Error in extract_specific_elements_from_urls task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Extraction error: {str(e)}"
            job.save()
        return None

@shared_task
def analyze_website_structure(job_id, user_id):
    """
    Analyze website structure based on mapped URLs
    """
    try:
        # Get user and API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        extraction_service = ExtractionService(firecrawl_service_api_key=firecrawl_api_key, user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # The URL to analyze is in the job query field
        url = job.query
        
        # Analyze website structure
        analysis_result = extraction_service.analyze_website_structure(url)
        
        # Save to scratchpad
        scratchpad_service.save(
            f"website_analysis_{job_id}", 
            analysis_result, 
            content_type="json"
        )
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url=url,
            title="Website Structure Analysis",
            content=json.dumps(analysis_result, indent=2),
            content_type="json",
            metadata={"type": "website_structure"}
        )
        
        # Update job status
        job.status = 'completed'
        job.completed_at = datetime.now()
        job.save()
        
        return analysis_result
        
    except Exception as e:
        # Log error
        print(f"Error in analyze_website_structure task: {str(e)}")
        if 'job' in locals():
            job.status = 'failed'
            job.error_message = f"Analysis error: {str(e)}"
            job.save()
        return None

@shared_task
def search_and_extract_data(job_id, user_id):
    """
    Search the web and extract structured data from results
    """
    try:
        # Get user and API key
        user = User.objects.get(id=user_id)
        firecrawl_api_key = user.firecrawl_key
        
        # Initialize services
        extraction_service = ExtractionService(firecrawl_service_api_key=firecrawl_api_key, user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Get search and extraction options
        options = job.options or {}
        
        # Search parameters
        limit = options.get("limit", 5)
        lang = options.get("lang", None)
        country = options.get("country", None)
        tbs = options.get("tbs", None)
        timeout = options.get("timeout", None)
        
        # Extraction parameters
        schema = options.get("extract_schema", None)
        prompt = options.get("extract_prompt", None)
        
        # Get agent configuration
        agent = options.get("agent", None)
        if agent:
            scratchpad_service.save("agent_config", f"Using AI agent: {agent.get('model', 'FIRE-1')} for search and extraction")
        
        # The search query is in the job query field
        query = job.query
        
        # Log the search query and parameters
        scratchpad_service.save("search_query", query)
        if lang or country:
            scratchpad_service.save("search_location", f"Language: {lang}, Country: {country}")
        if tbs:
            scratchpad_service.save("search_timeframe", tbs)
        
        # Perform search and extraction
        search_results = extraction_service.search_and_extract(
            query=query,
            schema=schema,
            prompt=prompt,
            limit=limit,
            lang=lang,
            country=country,
            tbs=tbs,
            timeout=timeout,
            agent=agent
        )
        
        # Save to scratchpad
        scratchpad_service.save(
            f"search_results_{job_id}", 
            search_results, 
            content_type="json"
        )
        
        # Create a result in the database for the overall search
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title=f"Search Results for: {query}",
            content=json.dumps(search_results, indent=2),
            content_type="json",
            metadata={"type": "search_with_extraction", "query": query}
        )
        
        # Store individual search results
        for i, result in enumerate(search_results.get("results", [])):
            # Store content
            if "content" in result:
                CrawlResult.objects.create(
                    crawl_job=job,
                    url=result.get("url", ""),
                    title=result.get("title", f"Result {i+1}"),
                    content=result.get("content", ""),
                    content_type="markdown",
                    metadata={"type": "search_result", "index": i}
                )
            
            # Store extraction if available
            if "extracted_data" in result:
                CrawlResult.objects.create(
                    crawl_job=job,
                    url=result.get("url", ""),
                    title=f"Extracted data from: {result.get('title', f'Result {i+1}')}",
                    content=json.dumps(result.get("extracted_data", {}), indent=2),
                    content_type="json",
                    metadata={"type": "search_extraction", "index": i}
                )
        
        # Update job status
        job.status = 'completed'
        job.completed_at = datetime.now()
        job.save()
        
        return search_results
        
    except Exception as e:
        # Log error
        print(f"Error in search_and_extract_data task: {str(e)}")
        if 'job' in locals():
            job.status = 'failed'
            job.error_message = f"Search and extraction error: {str(e)}"
            job.save()
        return None 