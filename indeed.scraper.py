import time
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def setup_driver():
    """Configure and return a Chrome WebDriver with automatic version matching"""
    options = Options()
    
    # Anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Headless mode settings
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")  # Suppress logging
    
    # Random user agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    try:
        # Automatic driver management with version matching
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Remove navigator.webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"Failed to setup driver: {str(e)}")
        return None

def scrape_indeed_jobs(job_title, location, max_results=10):
    base_url = "https://pk.indeed.com"
    jobs = []
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return []
        
        search_url = f"{base_url}/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+')}"
        print(f"Navigating to Indeed: {search_url}")
        
        driver.get(search_url)
        
        # Wait for job cards to load with longer timeout
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job_seen_beacon, .jobsearch-SerpJobCard"))
        )
        
        # Scroll to load more jobs
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
        
        # Parse the page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('div', class_='jobsearch-SerpJobCard')
        
        print(f"Found {len(job_cards)} job listings")
        
        for i, card in enumerate(job_cards[:max_results]):
            job = extract_job_data(card, base_url)
            if job:
                jobs.append(job)
                print(f"Scraped job {i+1}: {job['job_title']} at {job['company']}")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    return jobs

def extract_job_data(card, base_url):
    """Extract job details from a single job card"""
    job = {}
    
    try:
        # Job title
        title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jobtitle')
        job['job_title'] = title_elem.text.strip() if title_elem else "N/A"
        
        # Company
        company_elem = card.find('span', class_='companyName') or card.find('span', class_='company')
        job['company'] = company_elem.text.strip() if company_elem else "N/A"
        
        # Location
        location_elem = card.find('div', class_='companyLocation') or card.find('span', class_='location')
        job['location'] = location_elem.text.strip() if location_elem else "N/A"
        
        # Salary
        salary_elem = card.find('div', class_='metadata salary-snippet-container') or card.find('span', class_='salaryText')
        job['salary'] = salary_elem.text.strip() if salary_elem else "N/A"
        
        # Job nature (remote/onsite)
        job['jobNature'] = "onsite"
        remote_elems = card.find_all('span', class_='remote')
        if any('remote' in elem.text.lower() for elem in remote_elems):
            job['jobNature'] = "remote"
        
        # Experience (extracted from snippet)
        snippet_elem = card.find('div', class_='job-snippet') or card.find('div', class_='summary')
        job['experience'] = extract_experience(snippet_elem.text if snippet_elem else "")
        
        # Apply link
        link_elem = card.find('a', class_='jcs-JobTitle') or card.find('a', class_='jobtitle')
        if link_elem and 'href' in link_elem.attrs:
            job['apply_link'] = urljoin(base_url, link_elem['href'])
        else:
            job['apply_link'] = "N/A"
            
    except Exception as e:
        print(f"Error parsing job card: {str(e)}")
        return None
    
    return job

def extract_experience(text):
    """Extract experience requirements from text"""
    text = text.lower()
    if 'year' in text or 'yr' in text or 'experience' in text:
        return text.strip()
    return "N/A"

if __name__ == "__main__":
    # First install required packages:
    # pip install selenium webdriver-manager beautifulsoup4
    
    job_title = "Full Stack Developer"
    location = "Islamabad,Pakistan"
    
    print(f"\nScraping Indeed for '{job_title}' in '{location}'...")
    jobs = scrape_indeed_jobs(job_title, location, max_results=5)
    
    print("\nScraped Jobs:")
    print(json.dumps(jobs, indent=2, ensure_ascii=False))
    
    with open('indeed_jobs_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(jobs)} jobs to 'indeed_jobs_fixed.json'")