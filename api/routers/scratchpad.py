from fastapi import APIRouter, Depends, HTTPException, Query
from django.contrib.auth import get_user_model
from apps.scratchpad.models import ScratchpadEntry as DbScratchpadEntry
from api.models.scratchpad import ScratchpadEntry, ScratchpadResponse
from api.dependencies import get_current_user
from services.scratchpad_service import ScratchpadService
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/scratchpad")
User = get_user_model()

class EnhancedScratchpadEntry(BaseModel):
    key: str
    content: Any
    content_type: str = "text"
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ScratchpadSearchQuery(BaseModel):
    query: str
    k: int = 3
    filter_metadata: Optional[Dict[str, Any]] = None

class ScratchpadHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]

@router.post("/", response_model=ScratchpadResponse)
async def create_scratchpad_entry(entry: EnhancedScratchpadEntry, current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Create or update a scratchpad entry
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    db_entry = service.save(
        key=entry.key,
        content=entry.content,
        content_type=entry.content_type,
        source=entry.source,
        metadata=entry.metadata
    )
    
    return ScratchpadResponse(
        key=db_entry.key,
        content_type=db_entry.content_type,
        created_at=db_entry.created_at.isoformat(),
        updated_at=db_entry.updated_at.isoformat()
    )

@router.get("/{key}")
async def get_scratchpad_entry(key: str, current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Get a scratchpad entry by key
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    content, metadata = service.fetch(key)
    
    if content is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {
        "key": key,
        "content": content,
        "content_type": DbScratchpadEntry.objects.get(user=current_user, key=key).content_type,
        "metadata": metadata,
        "created_at": DbScratchpadEntry.objects.get(user=current_user, key=key).created_at.isoformat(),
        "updated_at": DbScratchpadEntry.objects.get(user=current_user, key=key).updated_at.isoformat()
    }

@router.post("/search")
async def semantic_search(search_query: ScratchpadSearchQuery, current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Perform semantic search on scratchpad entries
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    results = service.semantic_search(
        query=search_query.query,
        k=search_query.k,
        filter_metadata=search_query.filter_metadata
    )
    
    return {"results": results}

@router.get("/source/{source}")
async def get_by_source(source: str, current_user = Depends(get_current_user), limit: int = 10, session_id: Optional[str] = Query(None)):
    """
    Get scratchpad entries by source
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    entries = service.filter_by_source(source=source, limit=limit)
    
    return {"entries": entries}

@router.get("/session")
async def get_session_entries(current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Get all entries for the current session
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    entries = service.get_session_entries()
    
    return {"entries": entries}

@router.get("/", response_model=List[str])
async def list_scratchpad_keys(
    current_user = Depends(get_current_user), 
    session_id: Optional[str] = Query(None),
    source: Optional[str] = Query(None)
):
    """
    List all scratchpad keys for the current user
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    filter_metadata = {}
    if source:
        filter_metadata["source"] = source
    
    keys = service.list_keys(filter_metadata=filter_metadata if filter_metadata else None)
    return keys

@router.get("/history")
async def get_history(current_user = Depends(get_current_user), limit: Optional[int] = Query(None), session_id: Optional[str] = Query(None)):
    """
    Get history of scratchpad operations
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    history = service.get_history(limit=limit)
    
    return {"history": history}

@router.delete("/{key}")
async def delete_scratchpad_entry(key: str, current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Delete a scratchpad entry
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    success = service.delete(key)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
        
    return {"message": f"Entry with key '{key}' deleted successfully"}

@router.delete("/session/clear")
async def clear_session(current_user = Depends(get_current_user), session_id: Optional[str] = Query(None)):
    """
    Clear all entries for the current session
    """
    service = ScratchpadService(user_id=current_user.id, session_id=session_id)
    
    service.clear_session()
    
    return {"message": "Session cleared successfully"} 