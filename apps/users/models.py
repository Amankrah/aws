from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    api_key = models.CharField(max_length=64, blank=True)
    firecrawl_key = models.CharField(max_length=64, blank=True)
    anthropic_key = models.CharField(max_length=64, blank=True)
    usage_quota = models.IntegerField(default=100)
    usage_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username 