from celery import shared_task
from datetime import datetime
import json
import uuid

from apps.crawl_jobs.models import CrawlJob, CrawlResult
from services.claude_service import ClaudeService
from services.scratchpad_service import ScratchpadService
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def analyze_with_agent(job_id, user_id, question, context_keys=None):
    """
    Use Claude agent to analyze data and answer a specific question
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Initialize services
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Prepare the context by gathering data from scratchpad
        context = ""
        
        # If context_keys is provided, use those specific keys
        if context_keys:
            for key in context_keys:
                content = scratchpad_service.fetch(key)
                if content:
                    context += f"\n\n--- {key} ---\n{content}"
        else:
            # Otherwise, get all relevant keys from the scratchpad
            keys = scratchpad_service.list_keys()
            for key in keys:
                if any(key.startswith(prefix) for prefix in [
                    "search_content", "domain_results", "final_synthesis", 
                    "structured_data", "sentiment_analysis"
                ]):
                    content = scratchpad_service.fetch(key)
                    if content:
                        context += f"\n\n--- {key} ---\n{content}"
        
        # Build the prompt
        prompt = f"""
        Please analyze the following data and answer this specific question:
        
        Question: {question}
        
        Here is the information we've gathered:
        {context}
        
        Please provide a detailed and comprehensive answer based on the provided information.
        """
        
        # Get response from Claude
        analysis = claude_service.generate_response(prompt)
        
        # Save to scratchpad
        scratchpad_service.save(
            f"agent_analysis_{job_id}_{uuid.uuid4().hex[:8]}", 
            analysis
        )
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title=f"Agent Analysis: {question[:50] + '...' if len(question) > 50 else question}",
            content=analysis,
            content_type="markdown",
            metadata={"type": "agent_analysis", "question": question}
        )
        
        return analysis
        
    except Exception as e:
        # Log error
        print(f"Error in analyze_with_agent task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Agent analysis error: {str(e)}"
            job.save()
        return None

@shared_task
def summarize_content(job_id, user_id, content_keys=None, max_length=500):
    """
    Summarize content using Claude agent
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Initialize services
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Prepare the content to summarize
        content = ""
        
        # If content_keys is provided, use those specific keys
        if content_keys:
            for key in content_keys:
                key_content = scratchpad_service.fetch(key)
                if key_content:
                    content += f"\n\n--- {key} ---\n{key_content}"
        else:
            # Otherwise, use all results from the job
            results = CrawlResult.objects.filter(crawl_job_id=job.id)
            for result in results:
                if result.content_type == "markdown" and result.title != "Summary":
                    content += f"\n\n--- {result.title} ({result.url}) ---\n{result.content[:5000]}"
        
        # Build the prompt
        prompt = f"""
        Please summarize the following content in a concise but comprehensive way.
        The summary should be approximately {max_length} words in length.
        
        Content to summarize:
        {content}
        """
        
        # Get response from Claude
        summary = claude_service.generate_response(prompt)
        
        # Save to scratchpad
        scratchpad_service.save(f"summary_{job_id}", summary)
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title="Summary",
            content=summary,
            content_type="markdown",
            metadata={"type": "summary", "max_length": max_length}
        )
        
        return summary
        
    except Exception as e:
        # Log error
        print(f"Error in summarize_content task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Summarization error: {str(e)}"
            job.save()
        return None

@shared_task
def generate_action_plan(job_id, user_id, goal):
    """
    Generate an action plan to achieve a specific goal based on the gathered information
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)
        
        # Initialize services
        claude_service = ClaudeService(user=user)
        scratchpad_service = ScratchpadService(user_id=user_id)
        
        # Get job
        job = CrawlJob.objects.get(job_id=job_id)
        
        # Get the final synthesis or all relevant data
        synthesis = None
        try:
            synthesis_result = CrawlResult.objects.get(
                crawl_job_id=job.id,
                title="Final Synthesis"
            )
            synthesis = synthesis_result.content
        except CrawlResult.DoesNotExist:
            # If no synthesis exists, get all results
            results = CrawlResult.objects.filter(crawl_job_id=job.id)
            synthesis = "\n\n".join([
                f"--- {result.title} ({result.url}) ---\n{result.content[:2000]}"
                for result in results if result.content_type == "markdown"
            ])
        
        # Build the prompt
        prompt = f"""
        Based on the information below, please generate a detailed action plan to achieve the following goal:
        
        Goal: {goal}
        
        Information:
        {synthesis}
        
        Please provide:
        1. A step-by-step action plan
        2. Key resources needed
        3. Potential challenges and how to overcome them
        4. Metrics to track progress
        5. Timeline estimates
        """
        
        # Get response from Claude
        action_plan = claude_service.generate_response(prompt)
        
        # Save to scratchpad
        scratchpad_service.save(f"action_plan_{job_id}", action_plan)
        
        # Create a result in the database
        CrawlResult.objects.create(
            crawl_job=job,
            url="",
            title=f"Action Plan: {goal[:50] + '...' if len(goal) > 50 else goal}",
            content=action_plan,
            content_type="markdown",
            metadata={"type": "action_plan", "goal": goal}
        )
        
        return action_plan
        
    except Exception as e:
        # Log error
        print(f"Error in generate_action_plan task: {str(e)}")
        if 'job' in locals():
            job.error_message = f"Action plan generation error: {str(e)}"
            job.save()
        return None 