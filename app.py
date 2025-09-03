from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import asyncio
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import os
from typing import Optional

app = FastAPI(title="Indeed Job Extractor API", version="1.0.0")

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    url: str
    headless: bool = True

class JobResponse(BaseModel):
    success: bool
    job_id: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

class IndeedExtractor:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        
    def configure_webdriver(self):
        """Configure Chrome driver with stealth settings"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Use ChromeDriverManager for automatic driver management
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Apply stealth settings
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        return driver
    
    def start_driver(self):
        """Initialize the driver"""
        self.driver = self.configure_webdriver()
        return self.driver
    
    def close_driver(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def extract_job_id(self, url_str):
        """Extract job ID from Indeed URL"""
        try:
            match = re.search(r'[?&](?:jk|vjk)=([a-zA-Z0-9]+)', url_str)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def html_to_text(self, html):
        """Convert HTML to clean text with proper formatting"""
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Replace breaks with newlines
        for br in soup.find_all("br"):
            br.replace_with("\n")
        
        # Replace list items with bullet points
        for li in soup.find_all("li"):
            li.insert(0, "• ")
            li.append("\n")
        
        # Add spacing after block elements
        for tag in soup.find_all(['p', 'div', 'section', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.append("\n\n")
        
        text = soup.get_text()
        
        # Clean up text
        text = re.sub(r'\r', '', text)
        text = re.sub(r'[ \t\f\v]+', ' ', text)
        text = re.sub(r'\n[ \t]+', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def parse_json_ld_job_description(self, page_source):
        """Parse JSON-LD structured data for job description"""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    nodes = data if isinstance(data, list) else [data]
                    
                    for node in nodes:
                        if node.get('@type') == 'JobPosting' and 'description' in node:
                            return node['description']
                        
                        if '@graph' in node:
                            for graph_item in node['@graph']:
                                if graph_item.get('@type') == 'JobPosting' and 'description' in graph_item:
                                    return graph_item['description']
                except json.JSONDecodeError:
                    continue
                    
        except Exception:
            pass
        
        return None
    
    async def get_job_description(self, job_id, max_retries=2):
        """Extract job description using Selenium with multiple fallback strategies"""
        if not self.driver:
            self.start_driver()
        
        url = f"https://www.indeed.com/viewjob?jk={job_id}&hl=en"
        
        for attempt in range(max_retries):
            try:
                # Navigate to the job page
                self.driver.get(url)
                self.random_delay(2, 4)
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get page source for parsing
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Strategy 1: Classic jobDescriptionText selector
                job_desc_element = soup.find('div', id='jobDescriptionText')
                if job_desc_element:
                    return self.html_to_text(str(job_desc_element))
                
                # Strategy 2: JSON-LD structured data
                json_desc = self.parse_json_ld_job_description(page_source)
                if json_desc:
                    return self.html_to_text(json_desc)
                
                # Strategy 3: Modern Indeed selectors
                fallback_selectors = [
                    '[data-testid="jobDescription"]',
                    '.jobsearch-jobDescriptionText',
                    '.jobsearch-JobComponent-description',
                    '[class*="description"]'
                ]
                
                for selector in fallback_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element and element.text.strip():
                            return self.html_to_text(element.get_attribute('innerHTML'))
                    except NoSuchElementException:
                        continue
                
                # Strategy 4: Check if job is no longer available
                page_text = soup.get_text().lower()
                if any(phrase in page_text for phrase in [
                    'no longer available', 
                    'not accepting applications',
                    'job has expired',
                    'position filled'
                ]):
                    return "This job is no longer available on Indeed."
                
                if attempt < max_retries - 1:
                    self.random_delay(2, 4)
                
            except TimeoutException:
                if attempt < max_retries - 1:
                    self.random_delay(3, 5)
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.random_delay(2, 4)
        
        return "Could not extract job description after multiple attempts."

# Global extractor instance (reuse browser)
extractor = IndeedExtractor(headless=True)

@app.on_event("startup")
async def startup_event():
    """Initialize the browser on startup"""
    extractor.start_driver()

@app.on_event("shutdown")
async def shutdown_event():
    """Close the browser on shutdown"""
    extractor.close_driver()

@app.get("/")
async def root():
    return {
        "message": "Indeed Job Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "extract": "POST /extract - Extract job description from Indeed URL",
            "health": "GET /health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.post("/extract", response_model=JobResponse)
async def extract_job(request: JobRequest):
    start_time = time.time()
    
    try:
        # Extract job ID from URL
        job_id = extractor.extract_job_id(request.url)
        if not job_id:
            raise HTTPException(status_code=400, detail="Could not extract job ID from URL")
        
        # Extract job description
        description = await extractor.get_job_description(job_id)
        
        processing_time = time.time() - start_time
        
        return JobResponse(
            success=True,
            job_id=job_id,
            description=description,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return JobResponse(
            success=False,
            error=str(e),
            processing_time=round(processing_time, 2)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
