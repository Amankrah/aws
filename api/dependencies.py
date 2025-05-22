from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from django.contrib.auth import get_user_model
import os
import django
from asgiref.sync import sync_to_async

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

User = get_user_model()
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def get_current_user(api_key: str = Depends(API_KEY_HEADER)):
    """
    Authenticate user using API key
    """
    try:
        # Use sync_to_async to make Django ORM call
        get_user = sync_to_async(lambda: User.objects.get(api_key=api_key, is_active=True))
        user = await get_user()
        return user
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or inactive user",
            headers={"WWW-Authenticate": "ApiKey"},
        ) 