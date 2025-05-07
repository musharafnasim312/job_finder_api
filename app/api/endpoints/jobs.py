from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import asyncio

from pydantic import BaseModel
from app.models.job_models import JobSearchRequest, JobSearchResponse, JobListing
from app.services.linkedin_service import search_linkedin_jobs
from app.services.indeed_service import search_indeed_jobs
from app.services.jsearch_service import search_jsearch_jobs
from app.services.openai_service import filter_relevant_jobs

router = APIRouter()

@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(search_request: JobSearchRequest):
    """
    Search for jobs across multiple platforms based on the provided criteria
    """
    try:
        # Prepare search query from the request
        position_query = search_request.position
        location = search_request.location
        
        # Fetch jobs from all sources concurrently
        linkedin_task = search_linkedin_jobs(position_query, location)
        indeed_task = search_indeed_jobs(position_query, location)
        jsearch_task = search_jsearch_jobs(position_query, location)
        
        # Await all tasks
        jobs_results = await asyncio.gather(
            linkedin_task,
            indeed_task,
            jsearch_task
        )
        
        # Combine all job results
        all_jobs = []
        for jobs in jobs_results:
            all_jobs.extend(jobs)
        
        # Filter for relevant jobs using OpenAI
        relevant_jobs = await filter_relevant_jobs(all_jobs, search_request)
        
        # Limit to top results
        top_results = relevant_jobs[:20]  # Limit to top 20 relevant jobs
        
        # Convert to JobListing models
        job_listings = [JobListing(**job) for job in top_results]
        
        return JobSearchResponse(relevant_jobs=job_listings)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for jobs: {str(e)}")