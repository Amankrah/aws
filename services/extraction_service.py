from typing import Dict, List, Any, Optional
from services.claude_service import ClaudeService
from services.firecrawl_service import FirecrawlService
import json

class ExtractionService:
    def __init__(self, claude_service=None, firecrawl_service=None, firecrawl_service_api_key=None, user=None):
        self.user = user
        self.claude_service = claude_service or ClaudeService(user=user)
        self.firecrawl_service = firecrawl_service or FirecrawlService(api_key=firecrawl_service_api_key)
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        Extract clean text content from HTML
        """
        try:
            # Use Claude to extract clean text
            prompt = f"""
            Please extract the meaningful text content from this HTML, removing all markup, navigation, ads, and non-essential UI elements.
            Preserve the important information in a clean text format:

            {html_content[:10000]}  # Truncate for safety with large HTML
            """
            
            result = self.claude_service.generate_response(prompt)
            return result
        except Exception as e:
            print(f"Error extracting text from HTML: {str(e)}")
            return ""
    
    def extract_structured_data(self, content: str, schema: Dict) -> Dict:
        """
        Extract structured data according to a schema using Claude
        """
        try:
            # Use Claude to extract structured data
            extraction_result = self.claude_service.extract_structured_data(content, schema)
            
            # Ensure the result is valid JSON
            if isinstance(extraction_result, str):
                try:
                    return json.loads(extraction_result)
                except json.JSONDecodeError:
                    # If Claude didn't return valid JSON, try to extract JSON block
                    if "```json" in extraction_result:
                        json_block = extraction_result.split("```json")[1].split("```")[0]
                        return json.loads(json_block)
                    elif "{" in extraction_result and "}" in extraction_result:
                        # Simple heuristic to extract JSON
                        start = extraction_result.find("{")
                        end = extraction_result.rfind("}") + 1
                        return json.loads(extraction_result[start:end])
            
            return {}
        except Exception as e:
            print(f"Error extracting structured data: {str(e)}")
            return {}
    
    def extract_from_url(self, url: str, schema: Dict = None, prompt: str = None, agent: Dict = None) -> Dict:
        """
        Extract structured data directly from a URL using Firecrawl
        
        Args:
            url (str): The URL to extract data from
            schema (Dict): JSON schema for extraction
            prompt (str): Prompt for extraction without schema
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Extracted structured data
        """
        try:
            result = self.firecrawl_service.extract_structured_data(url, schema, prompt, agent=agent)
            
            # Process the results
            if "json" in result:
                return result["json"]
            elif "error" in result:
                print(f"Error extracting from URL: {result['error']}")
                return {}
            return result
        except Exception as e:
            print(f"Error extracting from URL: {str(e)}")
            return {}
    
    def batch_extract_from_urls(self, urls: List[str], schema: Dict = None, prompt: str = None, agent: Dict = None) -> Dict:
        """
        Extract structured data from multiple URLs using Firecrawl's batch capability
        
        Args:
            urls (List[str]): List of URLs to extract from
            schema (Dict): JSON schema for extraction
            prompt (str): Prompt for extraction without schema
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Mapping of URLs to extracted data
        """
        try:
            json_options = {}
            if schema:
                json_options["schema"] = schema
            elif prompt:
                json_options["prompt"] = prompt
                
            result = self.firecrawl_service.batch_scrape_urls(
                urls, 
                formats=["json"], 
                json_options=json_options,
                agent=agent
            )
            
            # Process the results
            extracted_data = {}
            if "data" in result:
                for i, item in enumerate(result["data"]):
                    if "json" in item:
                        url = urls[i] if i < len(urls) else f"url_{i}"
                        extracted_data[url] = item["json"]
            
            return extracted_data
        except Exception as e:
            print(f"Error batch extracting from URLs: {str(e)}")
            return {}
    
    def extract_specific_elements(self, url: str, selectors: List[str], agent: Dict = None) -> Dict[str, str]:
        """
        Extract specific elements from a webpage using selectors
        
        Args:
            url (str): The URL to extract from
            selectors (List[str]): CSS selectors for the elements to extract
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict[str, str]: Mapping of selectors to extracted text
        """
        try:
            # Use Firecrawl to extract specific elements
            actions = [
                {"type": "wait", "milliseconds": 2000},
                {"type": "scrape"}
            ]
            
            # For each selector, add an extraction task
            extraction_tasks = {}
            for selector in selectors:
                extraction_tasks[selector] = {"selector": selector}
            
            scrape_options = {
                "formats": ["html"],
                "extractors": extraction_tasks
            }
            
            result = self.firecrawl_service.scrape_url(
                url, 
                formats=["html"], 
                actions=actions,
                json_options={"extractors": extraction_tasks},
                agent=agent
            )
            
            # Process the results
            extracted_data = {}
            if "extractions" in result:
                for selector, data in result["extractions"].items():
                    extracted_data[selector] = data.get("text", "")
            
            return extracted_data
        except Exception as e:
            print(f"Error extracting elements from URL: {str(e)}")
            return {}
    
    def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment in the content
        """
        try:
            prompt = f"""
            Please analyze the sentiment of the following text. 
            Provide a score from -1 (very negative) to 1 (very positive) and a brief explanation:
            
            {content[:5000]}  # Limit content length
            
            Format your response as a JSON object with 'score' and 'explanation' fields.
            """
            
            result = self.claude_service.generate_response(prompt)
            
            # Parse the JSON response
            try:
                if "```json" in result:
                    json_str = result.split("```json")[1].split("```")[0]
                    return json.loads(json_str)
                else:
                    # Simple extraction if Claude didn't use code blocks
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start >= 0 and end > start:
                        return json.loads(result[start:end])
                    else:
                        # Fallback
                        return {
                            "score": 0,
                            "explanation": "Unable to determine sentiment from content."
                        }
            except json.JSONDecodeError:
                # Fallback if parsing fails
                return {
                    "score": 0,
                    "explanation": "Unable to parse sentiment analysis result."
                }
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {
                "score": 0,
                "explanation": f"Error: {str(e)}"
            } 
            
    def map_website(self, url: str, search: str = None, timeout: int = None) -> Dict[str, List[str]]:
        """
        Map a website to get all URLs
        
        Args:
            url (str): The URL to map
            search (str): Optional search term to filter the URLs by relevance
            timeout (int): Optional timeout in milliseconds
            
        Returns:
            Dict: Map results containing list of links
        """
        try:
            return self.firecrawl_service.map_url(url, search=search, timeout=timeout)
        except Exception as e:
            print(f"Error mapping website {url}: {str(e)}")
            return {"error": str(e), "links": []}
            
    def analyze_website_structure(self, url: str) -> Dict[str, Any]:
        """
        Analyze website structure based on mapped URLs
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            Dict: Analysis of website structure
        """
        try:
            # First map the website
            map_result = self.map_website(url)
            
            if "error" in map_result:
                return {"error": map_result["error"]}
                
            links = map_result.get("links", [])
            
            # Use Claude to analyze the structure
            prompt = f"""
            Analyze the structure of this website based on its URLs. Identify:
            1. Main sections/categories
            2. Content organization patterns
            3. Any SEO insights based on URL patterns
            
            URLs:
            {links[:100]}  # Limit to first 100 URLs for reasonable prompt size
            
            Format your response as a JSON object with 'sections', 'patterns', and 'seo_insights' fields.
            """
            
            result = self.claude_service.generate_response(prompt)
            
            # Parse the JSON response
            try:
                if "```json" in result:
                    json_str = result.split("```json")[1].split("```")[0]
                    analysis = json.loads(json_str)
                else:
                    # Simple extraction if Claude didn't use code blocks
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start >= 0 and end > start:
                        analysis = json.loads(result[start:end])
                    else:
                        # Fallback
                        analysis = {
                            "sections": [],
                            "patterns": [],
                            "seo_insights": "Unable to analyze website structure."
                        }
                        
                # Add the link count to the analysis
                analysis["link_count"] = len(links)
                analysis["sample_links"] = links[:10]  # Include some sample links
                
                return analysis
            except json.JSONDecodeError:
                # Fallback if parsing fails
                return {
                    "error": "Unable to parse website structure analysis result.",
                    "link_count": len(links),
                    "sample_links": links[:10]
                }
        except Exception as e:
            print(f"Error analyzing website structure for {url}: {str(e)}")
            return {
                "error": f"Error: {str(e)}",
                "link_count": 0,
                "sample_links": []
            }
            
    def search_and_extract(self, query: str, schema: Dict = None, prompt: str = None, 
                         limit: int = 5, lang: str = None, country: str = None, 
                         tbs: str = None, timeout: int = None, agent: Dict = None) -> Dict[str, Any]:
        """
        Search the web and extract structured data from search results
        
        Args:
            query (str): The search query
            schema (Dict): JSON schema for extraction
            prompt (str): Prompt for extraction without schema
            limit (int): Maximum number of search results
            lang (str): Language code (e.g., 'en', 'de', 'fr')
            country (str): Country code (e.g., 'us', 'de', 'fr')
            tbs (str): Time-based search parameter (e.g., 'qdr:h' for past hour)
            timeout (int): Timeout in milliseconds
            agent (Dict): AI agent configuration for intelligent navigation (model, prompt)
            
        Returns:
            Dict: Search results with extracted data
        """
        try:
            # Prepare scrape options with extraction settings
            scrape_options = {
                "formats": ["markdown", "json"]
            }
            
            # Configure extraction in scrape options
            json_options = {}
            if schema:
                json_options["schema"] = schema
            elif prompt:
                json_options["prompt"] = prompt
                
            if json_options:
                scrape_options["json_options"] = json_options
                
            # Add agent if provided
            if agent:
                scrape_options["agent"] = agent
            
            # Perform search with enhanced parameters
            search_results = self.firecrawl_service.search(
                query=query,
                limit=limit,
                scrape_options=scrape_options,
                lang=lang,
                country=country,
                tbs=tbs,
                timeout=timeout
            )
            
            # Process results to combine search and extraction
            processed_results = {
                "query": query,
                "results": []
            }
            
            # Handle any errors
            if "error" in search_results:
                processed_results["error"] = search_results["error"]
                return processed_results
                
            # Process each search result
            for result in search_results.get("data", []):
                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", "")
                }
                
                # Add extracted data if available
                if "json" in result:
                    processed_result["extracted_data"] = result["json"]
                
                # Add markdown content if available
                if "markdown" in result:
                    processed_result["content"] = result["markdown"]
                    
                processed_results["results"].append(processed_result)
                
            return processed_results
            
        except Exception as e:
            print(f"Error in search_and_extract for query '{query}': {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "results": []
            } 