from pydantic import BaseModel
from typing import List, Optional

class JobSearchRequest(BaseModel):
    position: str
    experience: str
    salary: str
    jobNature: str
    location: str
    skills: str

class JobListing(BaseModel):
    job_title: str
    company: str
    experience: str
    jobNature: str
    location: str
    salary: str = "Not specified"
    apply_link: str
    source: str  # LinkedIn, Indeed, or other source

class JobSearchResponse(BaseModel):
    relevant_jobs: List[JobListing]