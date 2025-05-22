from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from django.contrib.auth import get_user_model
import secrets
from api.dependencies import get_current_user
from pydantic import BaseModel
from asgiref.sync import sync_to_async

# Create Pydantic models for requests
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str

class ApiKeyUpdate(BaseModel):
    key: str

router = APIRouter(prefix="/auth", tags=["Authentication"])
User = get_user_model()

@router.post("/register")
async def register_user(user_data: UserRegistration):
    """
    Register a new user and generate API key
    """
    # Check if username exists
    username_exists = await sync_to_async(lambda: User.objects.filter(username=user_data.username).exists())()
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    email_exists = await sync_to_async(lambda: User.objects.filter(email=user_data.email).exists())()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Generate API key
    api_key = secrets.token_hex(32)
    
    # Create user
    await sync_to_async(
        lambda: User.objects.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            api_key=api_key
        )
    )()
    
    return {"username": user_data.username, "api_key": api_key}

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "usage_quota": current_user.usage_quota,
        "usage_count": current_user.usage_count,
        "firecrawl_key": current_user.firecrawl_key,
        "anthropic_key": current_user.anthropic_key
    }

@router.post("/refresh-key")
async def refresh_api_key(current_user = Depends(get_current_user)):
    """
    Generate a new API key for the current user
    """
    new_api_key = secrets.token_hex(32)
    
    # Update the user's API key
    def update_api_key():
        current_user.api_key = new_api_key
        current_user.save()
    
    await sync_to_async(update_api_key)()
    
    return {"api_key": new_api_key}

@router.post("/update-firecrawl-key")
async def update_firecrawl_key(key_data: ApiKeyUpdate, current_user = Depends(get_current_user)):
    """
    Update the user's Firecrawl API key
    """
    def update_key():
        current_user.firecrawl_key = key_data.key
        current_user.save()
    
    await sync_to_async(update_key)()
    
    return {"success": True}

@router.post("/update-anthropic-key")
async def update_anthropic_key(key_data: ApiKeyUpdate, current_user = Depends(get_current_user)):
    """
    Update the user's Anthropic API key
    """
    def update_key():
        current_user.anthropic_key = key_data.key
        current_user.save()
    
    await sync_to_async(update_key)()
    
    return {"success": True} 