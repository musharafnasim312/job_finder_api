import httpx
from typing import List, Dict, Any
from app.core.config import settings

async def search_jsearch_jobs(query: str, location: str) -> List[Dict[Any, Any]]:
    """
    Search for jobs using JSearch API (covers multiple sources including Glassdoor, ZipRecruiter, etc.)
    """
    url = settings.JSEARCH_API_URL
    
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": settings.JSEARCH_API_HOST
    }
    
    # Convert the search criteria to JSearch API format
    params = {
        "query": f"{query} in {location}",
        "page": "1",
        "num_pages": "1"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            raw_jobs = data.get("data", [])
            
            # Normalize the job data to our standard format
            normalized_jobs = []
            for job in raw_jobs:
                # Extract job nature
                job_nature = "Not specified"
                if job.get("job_employment_type"):
                    job_nature = job.get("job_employment_type")
                
                # Extract salary information
                salary = "Not specified"
                if job.get("job_min_salary") and job.get("job_max_salary"):
                    salary = f"{job.get('job_min_salary')} - {job.get('job_max_salary')} {job.get('job_salary_currency', '')}"
                elif job.get("job_salary_period") and job.get("job_salary"):
                    salary = f"{job.get('job_salary')} {job.get('job_salary_currency', '')} {job.get('job_salary_period')}"
                
                # Extract relevant information
                normalized_job = {
                    "job_title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "experience": job.get("job_required_experience", {}).get("required_experience_in_months", "Not specified"),
                    "jobNature": job_nature,
                    "location": job.get("job_city", "") + ", " + job.get("job_country", ""),
                    "salary": salary,
                    "apply_link": job.get("job_apply_link", ""),
                    "source": "JSearch",
                    "raw_description": job.get("job_description", "")
                }
                normalized_jobs.append(normalized_job)
                
            return normalized_jobs
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred with JSearch API: {e}")
        return []
    except Exception as e:
        print(f"Error fetching JSearch jobs: {e}")
        return []