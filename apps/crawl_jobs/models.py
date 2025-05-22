import uuid
from django.db import models

class CrawlJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    query = models.CharField(max_length=500)
    domain = models.CharField(max_length=255, blank=True)
    firecrawl_job_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    options = models.JSONField(blank=True, null=True, default=dict, help_text="Advanced scraping options including formats, proxy settings, extraction schema, map options, search parameters, and AI agent configuration for intelligent navigation")
    
    def __str__(self):
        return f"{self.user.username} - {self.query[:30]}"
    
class CrawlResult(models.Model):
    crawl_job = models.ForeignKey(CrawlJob, on_delete=models.CASCADE, related_name='results')
    url = models.URLField()
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    content_type = models.CharField(max_length=50)  # markdown, html, json
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.crawl_job} - {self.url[:30]}" 