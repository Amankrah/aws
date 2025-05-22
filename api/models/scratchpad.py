from pydantic import BaseModel, Field
from typing import Optional, Any, List

class ScratchpadEntry(BaseModel):
    key: str = Field(..., description="Unique key for the scratchpad entry")
    content: Any = Field(..., description="Content to be stored")
    content_type: str = Field("text", description="Type of content (text, json, binary)")
    
class ScratchpadResponse(BaseModel):
    key: str
    content_type: str
    created_at: str
    updated_at: str 