from django.contrib.auth import get_user_model
from apps.scratchpad.models import ScratchpadEntry
from typing import Dict, List, Any, Optional, Union
import uuid
import time
import json
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def sanitize_json_data(data):
    """Sanitize JSON data to remove non-serializable objects like functions."""
    if isinstance(data, dict):
        return {k: sanitize_json_data(v) for k, v in data.items() if not callable(v)}
    elif isinstance(data, list):
        return [sanitize_json_data(item) for item in data]
    elif callable(data):
        return str(data)
    elif isinstance(data, uuid.UUID):
        return str(data)
    else:
        return data

class ScratchpadService:
    def __init__(self, user_id=None, session_id=None):
        self.user_id = user_id
        self._user = None
        self.session_id = session_id or str(uuid.uuid4())
        
        # Create chroma directory if it doesn't exist
        persist_directory = os.path.join(os.getcwd(), "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize vector store for semantic search
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            embedding_function=self.embeddings, 
            collection_name=f"scratchpad_{self.session_id}",
            persist_directory=persist_directory
        )
        
        # Initialize memory for tracking history
        self._history = []
    
    @property
    def user(self):
        if self._user is None and self.user_id:
            self._user = User.objects.get(id=self.user_id)
        return self._user
    
    def save(self, key, content, content_type="text", source=None, metadata=None):
        """
        Save or update an entry in the scratchpad with enhanced metadata
        
        Args:
            key: Unique identifier for the entry
            content: The content to save
            content_type: Type of content (text, json, html, etc)
            source: Source of the information (company_domain, internet_search, agent)
            metadata: Additional metadata to store with the entry
        """
        if not self.user:
            raise ValueError("User is required")
            
        # Prepare metadata
        meta = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "source": source or "unknown",
        }
        
        if metadata:
            meta = {**meta, **sanitize_json_data(metadata)}
        
        # Process content based on type
        try:
            if content_type == "json" and not isinstance(content, str):
                # Sanitize JSON data and convert to JSON string
                content = sanitize_json_data(content)
                try:
                    content = json.dumps(content)
                except TypeError as e:
                    logger.error(f"Type error serializing content: {str(e)}")
                    content = str(content)
            elif content_type == "text" and not isinstance(content, str):
                # Convert non-string text content to string
                content = str(sanitize_json_data(content))
        except Exception as e:
            logger.error(f"Error processing content for storage: {str(e)}")
            # Fallback to string representation
            content = str(content)
            
        # Create or update the database entry
        entry, created = ScratchpadEntry.objects.update_or_create(
            user=self.user,
            key=key,
            defaults={
                'content_type': content_type,
                'text_content': content if content_type == "text" else "",
                'json_content': content if content_type == "json" else None,
                'metadata': meta
            }
        )
        
        # Add to vector store if it's text content
        if content_type == "text" and isinstance(content, str):
            try:
                self.vector_store.add_texts(
                    texts=[content],
                    metadatas=[{"key": key, **meta}]
                )
            except Exception as e:
                logger.error(f"Error adding to vector store: {str(e)}")
        
        # Add to history
        self._history.append({
            "operation": "save",
            "key": key,
            "timestamp": meta["timestamp"],
            "source": meta["source"]
        })
        
        return entry
    
    def fetch(self, key):
        """
        Fetch an entry from the scratchpad
        """
        if not self.user:
            raise ValueError("User is required")
            
        try:
            entry = ScratchpadEntry.objects.get(user=self.user, key=key)
            
            # Add to history
            self._history.append({
                "operation": "fetch",
                "key": key,
                "timestamp": datetime.now().isoformat()
            })
            
            if entry.content_type == "text":
                return entry.text_content, entry.metadata
            elif entry.content_type == "json":
                return entry.json_content, entry.metadata
            else:
                return None, entry.metadata
        except ScratchpadEntry.DoesNotExist:
            return None, None
    
    def semantic_search(self, query, k=3, filter_metadata=None):
        """
        Search for semantically similar content in the scratchpad
        
        Args:
            query: The search query
            k: Number of results to return
            filter_metadata: Optional filter to apply to metadata
            
        Returns:
            List of tuples containing (content, score, metadata)
        """
        try:
            # Add to history
            self._history.append({
                "operation": "semantic_search",
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Perform the search
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                key = doc.metadata.get("key")
                formatted_results.append({
                    "content": doc.page_content,
                    "score": score,
                    "key": key,
                    "metadata": doc.metadata
                })
                
            return formatted_results
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return []
    
    def filter_by_source(self, source, limit=10):
        """
        Filter entries by their source
        
        Args:
            source: Source to filter by (company_domain, internet_search, agent)
            limit: Maximum number of entries to return
            
        Returns:
            List of entries from the specified source
        """
        if not self.user:
            raise ValueError("User is required")
            
        entries = ScratchpadEntry.objects.filter(
            user=self.user
        ).order_by('-updated_at')[:limit]
        
        # Filter by source in metadata
        results = []
        for entry in entries:
            if entry.metadata and entry.metadata.get("source") == source:
                content = entry.text_content if entry.content_type == "text" else entry.json_content
                results.append({
                    "key": entry.key,
                    "content": content,
                    "content_type": entry.content_type,
                    "metadata": entry.metadata
                })
                
        return results
    
    def get_session_entries(self, session_id=None):
        """
        Get all entries for a specific session
        
        Args:
            session_id: Optional session ID (defaults to current session)
            
        Returns:
            List of entries from the session
        """
        if not self.user:
            raise ValueError("User is required")
            
        session = session_id or self.session_id
        
        entries = ScratchpadEntry.objects.filter(
            user=self.user
        ).order_by('-updated_at')
        
        # Filter by session ID in metadata
        results = []
        for entry in entries:
            if entry.metadata and entry.metadata.get("session_id") == session:
                content = entry.text_content if entry.content_type == "text" else entry.json_content
                results.append({
                    "key": entry.key,
                    "content": content,
                    "content_type": entry.content_type,
                    "metadata": entry.metadata
                })
                
        return results
    
    def list_keys(self, filter_metadata=None):
        """
        List all keys in the scratchpad, optionally filtering by metadata
        """
        if not self.user:
            raise ValueError("User is required")
            
        entries = ScratchpadEntry.objects.filter(user=self.user)
        
        if filter_metadata:
            filtered_entries = []
            for entry in entries:
                if entry.metadata:
                    match = True
                    for key, value in filter_metadata.items():
                        if entry.metadata.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_entries.append(entry)
            
            return [entry.key for entry in filtered_entries]
        
        return list(entries.values_list('key', flat=True))
    
    def delete(self, key):
        """
        Delete an entry from the scratchpad
        """
        if not self.user:
            raise ValueError("User is required")
            
        try:
            entry = ScratchpadEntry.objects.get(user=self.user, key=key)
            
            # Add to history
            self._history.append({
                "operation": "delete",
                "key": key,
                "timestamp": datetime.now().isoformat()
            })
            
            # Remove from vector store - this is a best effort, as we might not 
            # have the exact vector ID
            try:
                self.vector_store.delete(filter={"key": key})
            except Exception as e:
                print(f"Error deleting from vector store: {str(e)}")
                
            # Delete from database
            entry.delete()
            return True
        except ScratchpadEntry.DoesNotExist:
            return False
    
    def get_history(self, limit=None):
        """
        Get the history of operations performed on the scratchpad
        
        Args:
            limit: Optional limit on the number of history entries
            
        Returns:
            List of history entries
        """
        if limit:
            return self._history[-limit:]
        return self._history
    
    def clear_session(self):
        """
        Clear all entries for the current session
        """
        if not self.user:
            raise ValueError("User is required")
            
        # Get all entries for this session
        session_entries = self.get_session_entries()
        
        # Delete each entry
        for entry in session_entries:
            self.delete(entry["key"])
            
        # Clear history
        self._history = []
        
        # Clear vector store
        try:
            self.vector_store.delete(filter={"session_id": self.session_id})
        except Exception as e:
            print(f"Error clearing vector store: {str(e)}")
            
        return True 