import httpx
from typing import List, Dict, Any
from app.core.config import settings

async def search_linkedin_jobs(query: str, location: str) -> List[Dict[Any, Any]]:
    """
    Search for jobs on LinkedIn using RapidAPI's LinkedIn Jobs Search API
    """
    url = settings.LINKEDIN_API_URL
    
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.LINKEDIN_API_HOST
    }
    
    # Convert the search criteria to LinkedIn API format
    payload = {
        "search_terms": query,
        "location": location,
        "page": "1"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            raw_jobs = data.get("data", [])
            
            # Normalize the job data to our standard format
            normalized_jobs = []
            for job in raw_jobs:
                # Extract relevant information
                normalized_job = {
                    "job_title": job.get("job_title", ""),
                    "company": job.get("company_name", ""),
                    "experience": "Not specified",  # LinkedIn API doesn't always provide this
                    "jobNature": job.get("work_type", "Not specified"),
                    "location": job.get("location", ""),
                    "salary": job.get("salary", "Not specified"),
                    "apply_link": job.get("job_url", ""),
                    "source": "LinkedIn",
                    "raw_description": job.get("job_description", "")
                }
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred with LinkedIn API: {e}")
        return []
    except Exception as e:
        print(f"Error fetching LinkedIn jobs: {e}")
        return []