from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from uuid import UUID
from api.models.scraper import (
    ScrapeRequest, ScrapeResponse, JobStatusResponse, 
    BatchScrapeRequest, BatchScrapeResponse
)
from django.contrib.auth import get_user_model
from apps.crawl_jobs.models import CrawlJob, CrawlResult
from api.dependencies import get_current_user
from tasks.crawl_tasks import start_crawl_job, start_batch_scrape_job
from asgiref.sync import sync_to_async
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper")
User = get_user_model()

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Start a new scraping job with enhanced options for actions, formats, and structured data extraction
    """
    # Log request information
    logger.info(f"New scrape request: {request.query}, options: {request.__dict__}")
    
    # Check if user has reached quota
    credits_needed = 1
    # If using stealth proxy, increase credit cost
    if request.proxy == "stealth":
        credits_needed = 5
    
    if current_user.usage_count + credits_needed > current_user.usage_quota:
        raise HTTPException(
            status_code=403,
            detail=f"This request would exceed your usage quota. Need {credits_needed} credits."
        )
    
    # Create job and return job ID - wrap in sync_to_async
    @sync_to_async
    def create_job():
        try:
            # Convert request attributes to dict for storage
            options_dict = {
                "formats": request.formats,
                "actions": [action.dict() for action in request.actions] if request.actions else None,
                "location": request.location.dict() if request.location else None,
                "extract_schema": request.extract_schema,
                "extract_prompt": request.extract_prompt,
                "proxy": request.proxy,
                "retry_with_stealth": request.retry_with_stealth
            }
            
            # Add advanced options if provided
            if hasattr(request, 'agent') and request.agent:
                options_dict["agent"] = request.agent.dict() if hasattr(request.agent, 'dict') else request.agent
            if hasattr(request, 'max_depth'):
                options_dict["max_depth"] = request.max_depth
            if hasattr(request, 'allow_external_links'):
                options_dict["allow_external_links"] = request.allow_external_links
            if hasattr(request, 'only_main_content'):
                options_dict["only_main_content"] = request.only_main_content
            if hasattr(request, 'parse_pdf'):
                options_dict["parse_pdf"] = request.parse_pdf
            
            logger.info(f"Creating job with options: {options_dict}")
            
            job = CrawlJob.objects.create(
                user=current_user,
                query=request.query,
                domain=request.domain or "",
                status='pending',
                options=options_dict
            )
            
            # Increment usage count
            current_user.usage_count += credits_needed
            current_user.save()
            
            return job
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            raise
    
    job = await create_job()
    
    # Start background task
    logger.info(f"Starting crawl job: {job.job_id}")
    background_tasks.add_task(
        start_crawl_job, 
        job_id=str(job.job_id),
        user_id=current_user.id
    )
    
    # Create and validate response
    try:
        response = ScrapeResponse(job_id=job.job_id, status="pending")
        logger.info(f"Scrape request successful, job_id: {job.job_id}")
        # Test serialization
        json_response = json.dumps(response.dict())
        logger.debug(f"Serialized response: {json_response}")
        return response
    except Exception as e:
        logger.error(f"Error creating response: {str(e)}")
        # Return a manual dictionary to bypass the ScrapeResponse model
        return {"job_id": str(job.job_id), "status": "pending"}

@router.post("/batch", response_model=BatchScrapeResponse)
async def batch_scrape_urls(
    request: BatchScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Start a new batch scraping job for multiple URLs
    """
    # Calculate credits needed (5 per URL if using stealth proxy)
    credits_per_url = 5 if request.proxy == "stealth" else 1
    total_credits_needed = len(request.urls) * credits_per_url
    
    # Check if user has reached quota
    if current_user.usage_count + total_credits_needed > current_user.usage_quota:
        raise HTTPException(
            status_code=403,
            detail=f"This batch would exceed your usage quota. Need {total_credits_needed} credits."
        )
    
    # Create job and return job ID - wrap in sync_to_async
    @sync_to_async
    def create_batch_job():
        job = CrawlJob.objects.create(
            user=current_user,
            query=f"Batch scrape of {len(request.urls)} URLs",
            status='pending',
            options={
                "urls": request.urls,
                "formats": request.formats,
                "extract_schema": request.extract_schema,
                "extract_prompt": request.extract_prompt,
                "batch": True,
                "proxy": request.proxy,
                "retry_with_stealth": request.retry_with_stealth
            }
        )
        
        # Increment usage count
        current_user.usage_count += total_credits_needed
        current_user.save()
        
        return job
    
    job = await create_batch_job()
    
    # Start background task
    background_tasks.add_task(
        start_batch_scrape_job, 
        job_id=str(job.job_id),
        user_id=current_user.id
    )
    
    return BatchScrapeResponse(job_id=job.job_id, status="pending")

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID, current_user = Depends(get_current_user)):
    """
    Get the status of a scraping job
    """
    logger.info(f"Get job status request: {job_id}")
    
    @sync_to_async
    def get_job():
        try:
            return CrawlJob.objects.get(job_id=job_id, user=current_user)
        except CrawlJob.DoesNotExist:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
    
    job = await get_job()
    
    logger.info(f"Retrieved job {job_id}, status: {job.status}, error: {job.error_message}")
    
    try:
        response = JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            error_message=job.error_message if job.status == "failed" else None
        )
        # Test serialization
        json_response = json.dumps(response.dict())
        logger.debug(f"Serialized job status response: {json_response}")
        return response
    except Exception as e:
        logger.error(f"Error creating job status response: {str(e)}")
        # Return a manual dictionary to bypass the model
        return {
            "job_id": str(job.job_id),
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message if job.status == "failed" else None
        }

@router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: UUID, current_user = Depends(get_current_user)):
    """
    Get the results of a completed scraping job
    """
    @sync_to_async
    def get_job_and_results():
        try:
            job = CrawlJob.objects.get(job_id=job_id, user=current_user)
            
            if job.status != "completed":
                raise HTTPException(status_code=400, detail=f"Job is not completed yet. Current status: {job.status}")
            
            results = []
            for result in job.results.all():
                results.append({
                    "url": result.url,
                    "title": result.title,
                    "content": result.content,
                    "content_type": result.content_type,
                    "metadata": result.metadata
                })
            
            return job, results
        except CrawlJob.DoesNotExist:
            raise HTTPException(status_code=404, detail="Job not found")
    
    job, results = await get_job_and_results()
    
    return {
        "job_id": job.job_id,
        "query": job.query,
        "domain": job.domain,
        "results": results
    } 