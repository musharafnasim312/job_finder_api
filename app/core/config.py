import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Job Finder API"
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    
    # RapidAPI Host URLs
    LINKEDIN_API_HOST: str = "linkedin-jobs-search.p.rapidapi.com"
    INDEED_API_HOST: str = "indeed-api.p.rapidapi.com"
    JSEARCH_API_HOST: str = "jsearch.p.rapidapi.com"
    
    # API Endpoints
    LINKEDIN_API_URL: str = "https://linkedin-jobs-search.p.rapidapi.com/"
    INDEED_API_URL: str = "https://indeed-api.p.rapidapi.com/search"
    JSEARCH_API_URL: str = "https://jsearch.p.rapidapi.com/search"
    
    # OpenAI Configuration
    OPENAI_MODEL: str = "gpt-4o"  # You can use gpt-3.5-turbo for lower cost

settings = Settings()