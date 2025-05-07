import httpx
from typing import List, Dict, Any
from app.core.config import settings

async def search_indeed_jobs(query: str, location: str) -> List[Dict[Any, Any]]:
    """
    Search for jobs on Indeed using RapidAPI's Indeed API
    """
    url = settings.INDEED_API_URL
    
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.INDEED_API_HOST
    }
    
    # Convert the search criteria to Indeed API format
    params = {
        "query": query,
        "location": location,
        "page": "1",
        "sort_by": "relevance"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            raw_jobs = data.get("hits", [])
            
            # Normalize the job data to our standard format
            normalized_jobs = []
            for job in raw_jobs:
                # Extract job details
                job_detail = job.get("hit", {})
                
                # Extract relevant information
                normalized_job = {
                    "job_title": job_detail.get("title", ""),
                    "company": job_detail.get("company", {}).get("name", ""),
                    "experience": job_detail.get("experience", "Not specified"),
                    "jobNature": job_detail.get("workType", "Not specified"),
                    "location": job_detail.get("location", {}).get("displayName", ""),
                    "salary": job_detail.get("compensation", "Not specified"),
                    "apply_link": job_detail.get("viewJobLink", ""),
                    "source": "Indeed",
                    "raw_description": job_detail.get("description", "")
                }
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred with Indeed API: {e}")
        return []
    except Exception as e:
        print(f"Error fetching Indeed jobs: {e}")
        return []