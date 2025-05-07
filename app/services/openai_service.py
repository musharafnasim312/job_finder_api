import openai
from typing import List, Dict, Any
from app.core.config import settings
from app.models.job_models import JobSearchRequest

# Configure OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

async def filter_relevant_jobs(jobs: List[Dict[Any, Any]], search_criteria: JobSearchRequest) -> List[Dict[Any, Any]]:
    """
    Use OpenAI to analyze job descriptions and filter for relevance based on search criteria
    """
    if not jobs:
        return []
    
    relevant_jobs = []
    
    # Prepare the search criteria as a string
    criteria_string = f"""
    Position: {search_criteria.position}
    Experience: {search_criteria.experience}
    Salary: {search_criteria.salary}
    Job Nature: {search_criteria.jobNature}
    Location: {search_criteria.location}
    Skills: {search_criteria.skills}
    """
    
    for job in jobs:
        # Skip jobs with no description
        if not job.get("raw_description"):
            continue
        
        # Create a prompt for OpenAI
        prompt = f"""
        Task: Analyze if the job listing below is relevant to the given search criteria.
        
        Search Criteria:
        {criteria_string}
        
        Job Listing:
        Job Title: {job.get('job_title', '')}
        Company: {job.get('company', '')}
        Location: {job.get('location', '')}
        Job Type: {job.get('jobNature', '')}
        Description: {job.get('raw_description', '')}
        
        Instructions:
        1. Analyze if this job matches the position, experience level, and skills required.
        2. Check if the job location matches or is remote if that was specified.
        3. Determine if the job nature (onsite/remote/hybrid) aligns with the criteria.
        4. Provide a relevance score from 0 to 100, where:
           - 0-30: Not relevant
           - 31-70: Somewhat relevant
           - 71-100: Highly relevant
        
        Please respond with ONLY a JSON object in this format:
        {{"relevance_score": <score>, "is_relevant": <true/false>}}
        """
        
        try:
            # Call OpenAI API
            response = await openai.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a job matching assistant that analyzes job listings for relevance to search criteria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Low temperature for more deterministic results
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract the JSON part if there's any text before or after
            import json
            import re
            
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group(0))
            else:
                # If no JSON found, default to not relevant
                result_json = {"relevance_score": 0, "is_relevant": False}
            
            # Check if the job is relevant
            if result_json.get("is_relevant", False):
                # Remove raw description as it's no longer needed
                if "raw_description" in job:
                    del job["raw_description"]
                
                # Add relevance score
                job["relevance_score"] = result_json.get("relevance_score", 0)
                
                relevant_jobs.append(job)
                
        except Exception as e:
            print(f"Error with OpenAI analysis: {e}")
            # If there's an error, add the job anyway but with a lower relevance score
            if "raw_description" in job:
                del job["raw_description"]
            job["relevance_score"] = 50  # Neutral score
            relevant_jobs.append(job)
    
    # Sort by relevance score (highest first)
    relevant_jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Remove relevance score from the final output
    for job in relevant_jobs:
        if "relevance_score" in job:
            del job["relevance_score"]
    
    return relevant_jobs