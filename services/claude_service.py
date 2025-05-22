import anthropic
from django.conf import settings
from typing import Dict, List, Any, Optional, Union
import time
import uuid

class ClaudeService:
    def __init__(self, api_key=None, user=None):
        # Check for user-specific API key first, then passed key, then settings
        if user and user.anthropic_key:
            self.api_key = user.anthropic_key
        else:
            self.api_key = api_key or settings.ANTHROPIC_API_KEY
            
        # Ensure API key is explicitly set in the client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-7-sonnet-20250219"
    
    def generate_response(self, prompt, max_tokens=2000, system=None, thinking=None):
        """
        Generate a response from Claude
        
        Args:
            prompt: The user prompt to send to Claude
            max_tokens: Maximum number of tokens in the response (default: 2000)
            system: Optional system prompt to set context
            thinking: Optional dict with 'type' and 'budget_tokens' for extended thinking
                      Example: {'type': 'enabled', 'budget_tokens': 16000}
        """
        try:
            messages = []
            
            if system:
                messages.append({"role": "system", "content": system})
                
            messages.append({"role": "user", "content": prompt})
            
            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
            # Add thinking parameter if provided
            if thinking:
                params["thinking"] = thinking
            
            # Create a new client instance with explicit API key for this request
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(**params)
            
            return response.content[0].text
        except Exception as e:
            print(f"Error generating response from Claude: {str(e)}")
            return f"Error: {str(e)}"
    
    def analyze_content(self, content, question, max_tokens=2000, thinking=None):
        """
        Analyze content with a specific question
        
        Args:
            content: The content to analyze
            question: The question to answer about the content
            max_tokens: Maximum number of tokens in the response
            thinking: Optional dict with 'type' and 'budget_tokens' for extended thinking
        """
        prompt = f"""
        I need you to analyze the following content and answer a question about it:
        
        Content:
        {content}
        
        Question:
        {question}
        
        Please provide a comprehensive answer based solely on the content provided.
        """
        
        return self.generate_response(prompt, max_tokens, thinking=thinking)
    
    def extract_structured_data(self, content, schema, max_tokens=2000, thinking=None):
        """
        Extract structured data according to a schema
        
        Args:
            content: The content to extract data from
            schema: The schema to extract according to
            max_tokens: Maximum number of tokens in the response
            thinking: Optional dict with 'type' and 'budget_tokens' for extended thinking
        """
        schema_str = str(schema)
        
        prompt = f"""
        I need you to extract structured data from the following content according to this schema:
        
        Schema:
        {schema_str}
        
        Content:
        {content}
        
        Please provide the extracted data in valid JSON format that follows the schema.
        """
        
        return self.generate_response(prompt, max_tokens, thinking=thinking)
        
    def create_batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a batch of message requests to be processed asynchronously.
        
        Args:
            requests: A list of request objects, where each object contains:
                - custom_id: A unique identifier for the request
                - params: The parameters for the message request
                
        Returns:
            Dict containing batch information including the batch ID and status
        """
        try:
            # Format the batch request according to Anthropic's API
            batch_requests = []
            for req in requests:
                custom_id = req.get("custom_id", f"req_{uuid.uuid4().hex[:8]}")
                params = req.get("params", {})
                
                # Ensure model is specified
                if "model" not in params:
                    params["model"] = self.model
                    
                batch_requests.append({
                    "custom_id": custom_id,
                    "params": params
                })
            
            # Create the batch
            response = self.client.messages.batches.create(
                requests=batch_requests
            )
            
            return {
                "id": response.id,
                "type": response.type,
                "processing_status": response.processing_status,
                "request_counts": response.request_counts,
                "created_at": response.created_at,
                "expires_at": response.expires_at,
                "results_url": response.results_url
            }
        except Exception as e:
            print(f"Error creating batch: {str(e)}")
            return {"error": str(e)}
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Check the status of a batch.
        
        Args:
            batch_id: The ID of the batch to check
            
        Returns:
            Dict containing the batch status information
        """
        try:
            response = self.client.messages.batches.retrieve(
                batch_id=batch_id
            )
            
            return {
                "id": response.id,
                "type": response.type,
                "processing_status": response.processing_status,
                "request_counts": response.request_counts,
                "created_at": response.created_at,
                "expires_at": response.expires_at,
                "ended_at": response.ended_at,
                "results_url": response.results_url
            }
        except Exception as e:
            print(f"Error getting batch status: {str(e)}")
            return {"error": str(e)}
    
    def get_batch_results(self, batch_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed batch.
        
        Args:
            batch_id: The ID of the batch to get results for
            
        Returns:
            Dict containing the batch results, keyed by custom_id
        """
        try:
            # First get the batch to check if it's complete
            batch = self.get_batch_status(batch_id)
            
            if "error" in batch:
                return batch
                
            if batch["processing_status"] != "ended":
                return {
                    "error": "Batch processing has not ended yet",
                    "status": batch["processing_status"],
                    "request_counts": batch["request_counts"]
                }
                
            if not batch["results_url"]:
                return {
                    "error": "Results URL not available",
                    "status": batch["processing_status"]
                }
                
            # Fetch results from the results URL
            import requests
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.get(batch["results_url"], headers=headers)
            
            if response.status_code != 200:
                return {
                    "error": f"Failed to fetch results: {response.status_code}",
                    "details": response.text
                }
                
            # Process the JSONL response
            results = {}
            for line in response.text.strip().split('\n'):
                if not line:
                    continue
                    
                import json
                result = json.loads(line)
                custom_id = result.get("custom_id")
                
                if custom_id:
                    results[custom_id] = result.get("result")
                    
            return {
                "batch_id": batch_id,
                "results": results,
                "completed": batch["request_counts"]["succeeded"],
                "errors": batch["request_counts"]["errored"],
                "expired": batch["request_counts"]["expired"],
                "canceled": batch["request_counts"]["canceled"]
            }
        except Exception as e:
            print(f"Error getting batch results: {str(e)}")
            return {"error": str(e)}
            
    def wait_for_batch_completion(self, batch_id: str, max_wait_time=3600, poll_interval=10) -> Dict[str, Any]:
        """
        Wait for a batch to complete, polling at the specified interval.
        
        Args:
            batch_id: The ID of the batch to wait for
            max_wait_time: Maximum time to wait in seconds (default: 1 hour)
            poll_interval: Time between status checks in seconds (default: 10 seconds)
            
        Returns:
            Dict containing the batch results
        """
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            status = self.get_batch_status(batch_id)
            
            if "error" in status:
                return status
                
            if status["processing_status"] == "ended":
                return self.get_batch_results(batch_id)
                
            # Wait before polling again
            time.sleep(poll_interval)
            
        return {
            "error": "Max wait time exceeded",
            "batch_id": batch_id,
            "status": self.get_batch_status(batch_id)
        }
    
    def analyze_code(self, code, question, max_tokens=4000, budget_tokens=16000):
        """
        Analyze code with extended thinking capabilities to perform deep analysis
        and provide detailed reasoning for complex code questions.
        
        Args:
            code: The code snippet or file to analyze
            question: Specific question to answer about the code
            max_tokens: Maximum tokens for response (default: 4000)
            budget_tokens: Number of tokens allocated for thinking (default: 16000)
            
        Returns:
            Dict containing full response with thinking blocks and text blocks
        """
        try:
            prompt = f"""
            Analyze the following code and answer the question:
            
            ```
            {code}
            ```
            
            Question: {question}
            
            Please provide a detailed analysis with your thought process.
            """
            
            # Enable extended thinking
            thinking = {
                "type": "enabled",
                "budget_tokens": budget_tokens
            }
            
            # Get full response (not just content[0].text) to preserve thinking blocks
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                thinking=thinking,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Return full response object to allow access to thinking blocks
            return {
                "text": response.content[-1].text if response.content else "",
                "full_response": response
            }
        except Exception as e:
            print(f"Error analyzing code with extended thinking: {str(e)}")
            return {"error": str(e)}
    
    def chat_with_thinking(self, messages, max_tokens=2000, budget_tokens=16000, system=None):
        """
        Conduct a multi-turn conversation with extended thinking capabilities.
        
        Args:
            messages: List of conversation messages in the format:
                     [{"role": "user", "content": "..."}, {"role": "assistant", "content": [...]}, ...]
            max_tokens: Maximum tokens for response (default: 2000)
            budget_tokens: Number of tokens allocated for thinking (default: 16000)
            system: Optional system prompt
            
        Returns:
            Dict containing full response with thinking blocks preserved
        """
        try:
            # Enable extended thinking
            thinking = {
                "type": "enabled",
                "budget_tokens": budget_tokens
            }
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "thinking": thinking,
                "messages": messages
            }
            
            # Add system message if provided
            if system:
                params["system"] = system
                
            # Get full response to preserve thinking blocks
            response = self.client.messages.create(**params)
            
            # Return both the text response and full response object with thinking blocks
            return {
                "text": next((block.text for block in response.content if block.type == "text"), ""),
                "full_response": response
            }
        except Exception as e:
            print(f"Error in conversation with extended thinking: {str(e)}")
            return {"error": str(e)}
    
    def thinking_with_tools(self, messages, tools, max_tokens=4000, budget_tokens=16000, system=None):
        """
        Use extended thinking capabilities with tool use to enhance reasoning during tool calls.
        
        Args:
            messages: List of conversation messages
            tools: List of tool definitions
            max_tokens: Maximum tokens for response (default: 4000)
            budget_tokens: Number of tokens allocated for thinking (default: 16000)
            system: Optional system prompt
            
        Returns:
            Dict containing full response with thinking blocks and tool use blocks
        """
        try:
            # Enable extended thinking
            thinking = {
                "type": "enabled",
                "budget_tokens": budget_tokens
            }
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "thinking": thinking,
                "messages": messages,
                "tools": tools
            }
            
            # Add system message if provided
            if system:
                params["system"] = system
                
            # Get full response to preserve thinking blocks and tool use blocks
            response = self.client.messages.create(**params)
            
            # Extract blocks by type
            thinking_blocks = [block for block in response.content if block.type in ["thinking", "redacted_thinking"]]
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block for block in response.content if block.type == "text"]
            
            return {
                "text": next((block.text for block in text_blocks), ""),
                "thinking_blocks": thinking_blocks,
                "tool_use_blocks": tool_use_blocks,
                "full_response": response
            }
        except Exception as e:
            print(f"Error using tools with extended thinking: {str(e)}")
            return {"error": str(e)} 