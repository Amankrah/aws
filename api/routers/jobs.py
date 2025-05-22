from fastapi import APIRouter, Depends, HTTPException
from django.contrib.auth import get_user_model
from apps.crawl_jobs.models import CrawlJob
from api.models.jobs import JobListItem, JobDetail
from api.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/jobs")
User = get_user_model()

@router.get("/", response_model=List[JobListItem])
async def list_jobs(current_user = Depends(get_current_user)):
    """
    List all jobs for the current user
    """
    jobs = CrawlJob.objects.filter(user=current_user).order_by('-created_at')
    
    return [
        JobListItem(
            job_id=job.job_id,
            query=job.query,
            status=job.status,
            created_at=job.created_at
        ) for job in jobs
    ]

@router.get("/{job_id}", response_model=JobDetail)
async def get_job_detail(job_id: str, current_user = Depends(get_current_user)):
    """
    Get detailed information about a job
    """
    try:
        job = CrawlJob.objects.get(job_id=job_id, user=current_user)
    except CrawlJob.DoesNotExist:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Count results
    result_count = job.results.count()
    
    return JobDetail(
        job_id=job.job_id,
        query=job.query,
        domain=job.domain,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message if job.status == "failed" else None,
        result_count=result_count
    )

@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user = Depends(get_current_user)):
    """
    Delete a job and all its results
    """
    try:
        job = CrawlJob.objects.get(job_id=job_id, user=current_user)
        job.delete()
        return {"message": f"Job with ID '{job_id}' deleted successfully"}
    except CrawlJob.DoesNotExist:
        raise HTTPException(status_code=404, detail="Job not found") 