"""
Job Fetcher - Retrieve job listings from Adzuna API
"""
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import requests
import redis
from loguru import logger

from app.models import JobPosting, ContractType
from app.config import settings


class JobFetcher:
    """Fetch and cache job listings from Adzuna API"""

    def __init__(self):
        """Initialize the job fetcher with API credentials and cache"""
        # Validate Adzuna credentials
        if not settings.has_adzuna_credentials:
            raise ValueError(
                "Adzuna credentials not found! "
                "Please set ADZUNA_APP_ID and ADZUNA_API_KEY in .env"
            )

        self.app_id = settings.adzuna_app_id
        self.api_key = settings.adzuna_api_key
        self.base_url = settings.adzuna_base_url
        self.country = settings.adzuna_country

        # Setup Redis cache if enabled
        self.cache_enabled = settings.enable_cache
        if self.cache_enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis cache connected")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
                self.cache_enabled = False
        else:
            logger.info("Cache disabled by configuration")

        logger.info(f"JobFetcher initialized for country: {self.country}")

    def _generate_cache_key(self, query: str, location: str, params: Dict) -> str:
        """Generate a unique cache key based on search parameters"""
        # Create a string representation of all parameters
        cache_data = {
            "query": query,
            "location": location,
            "country": self.country,
            **params
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        # Hash it to create a short key
        return f"jobs:{hashlib.md5(cache_string.encode()).hexdigest()}"

    def _get_from_cache(self, cache_key: str) -> Optional[List[JobPosting]]:
        """Retrieve jobs from Redis cache"""
        if not self.cache_enabled:
            return None

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.info(f"📦 Cache HIT: {cache_key}")
                jobs_data = json.loads(cached_data)
                return [JobPosting(**job) for job in jobs_data]
            else:
                logger.debug(f"Cache MISS: {cache_key}")
                return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def _save_to_cache(self, cache_key: str, jobs: List[JobPosting]):
        """Save jobs to Redis cache"""
        if not self.cache_enabled:
            return

        try:
            # Convert JobPosting objects to dict for JSON serialization
            jobs_data = [job.model_dump(mode='json') for job in jobs]
            self.redis_client.setex(
                cache_key,
                settings.cache_ttl,
                json.dumps(jobs_data, default=str)
            )
            logger.info(f"💾 Cached {len(jobs)} jobs with TTL={settings.cache_ttl}s")
        except Exception as e:
            logger.error(f"Cache save error: {e}")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """Make API request to Adzuna with error handling"""
        url = f"{self.base_url}/{endpoint}"

        # Add authentication
        params['app_id'] = self.app_id
        params['app_key'] = self.api_key

        logger.debug(f"API Request: {url} with params: {params}")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def _parse_contract_type(self, contract_time: Optional[str]) -> Optional[ContractType]:
        """Parse Adzuna contract_time to our ContractType enum"""
        if not contract_time:
            return None

        contract_time = contract_time.lower()

        if 'full' in contract_time:
            return ContractType.FULL_TIME
        elif 'part' in contract_time:
            return ContractType.PART_TIME
        elif 'contract' in contract_time:
            return ContractType.CONTRACT
        elif 'temp' in contract_time:
            return ContractType.TEMPORARY
        elif 'intern' in contract_time:
            return ContractType.INTERNSHIP
        elif 'freelance' in contract_time:
            return ContractType.FREELANCE
        else:
            return ContractType.OTHER

    def _parse_date(self, date_string: Optional[str]) -> Optional[date]:
        """Parse Adzuna date string to Python date object"""
        if not date_string:
            return None

        try:
            # Adzuna typically uses ISO format: "2024-10-01T12:00:00Z"
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.date()
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse date: {date_string} - {e}")
            return None

    def _parse_job(self, job_data: Dict) -> JobPosting:
        """Convert Adzuna API response to JobPosting object"""
        # Extract salary information
        salary_min = job_data.get('salary_min')
        salary_max = job_data.get('salary_max')
        salary_currency = None

        # Try to determine currency from location or use default
        if salary_min or salary_max:
            location = job_data.get('location', {})
            country = location.get('area', [])
            if country and 'US' in str(country):
                salary_currency = 'USD'
            elif country and any(eu in str(country) for eu in ['Belgium', 'France', 'Germany']):
                salary_currency = 'EUR'
            elif country and 'UK' in str(country):
                salary_currency = 'GBP'
            else:
                salary_currency = 'EUR'  # Default

        # Build location string
        location_obj = job_data.get('location', {})
        location_parts = location_obj.get('display_name', '').split(',')
        location_str = ', '.join(part.strip() for part in location_parts if part.strip())

        return JobPosting(
            job_title=job_data.get('title', 'Unknown Title'),
            company_name=job_data.get('company', {}).get('display_name', 'Unknown Company'),
            description=job_data.get('description', ''),
            location=location_str or 'Unknown Location',
            job_url=job_data.get('redirect_url', ''),
            redirect_url=job_data.get('redirect_url'),
            posted_date=self._parse_date(job_data.get('created')),
            contract_type=self._parse_contract_type(job_data.get('contract_time')),
            category=job_data.get('category', {}).get('label'),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            adzuna_job_id=job_data.get('id'),
            # Matching fields will be populated by the matcher later
            match_score=None,
            match_explanation=None,
            required_skills=None
        )

    def search_jobs(
        self,
        query: str,
        location: str = "",
        results_per_page: int = 50,
        page: int = 1,
        sort_by: str = "relevance",
        **kwargs
    ) -> List[JobPosting]:
        """
        Search for jobs on Adzuna

        Args:
            query: Job title or keywords to search for
            location: Location string (city, region, country)
            results_per_page: Number of results per page (max 50)
            page: Page number (default 1)
            sort_by: Sort order - 'relevance', 'date', or 'salary'
            **kwargs: Additional Adzuna API parameters

        Returns:
            List of JobPosting objects
        """
        logger.info(f"🔍 Searching jobs: query='{query}', location='{location}'")

        # Validate results_per_page
        if results_per_page > 50:
            logger.warning(f"results_per_page capped at 50 (requested: {results_per_page})")
            results_per_page = 50

        # Build API parameters
        params = {
            'results_per_page': results_per_page,
            'what': query,
            'where': location,
            'sort_by': sort_by,
            **kwargs
        }

        # Check cache first
        cache_key = self._generate_cache_key(query, location, params)
        cached_jobs = self._get_from_cache(cache_key)
        if cached_jobs:
            return cached_jobs

        # Make API request
        try:
            endpoint = f"jobs/{self.country}/search/{page}"
            response_data = self._make_request(endpoint, params)

            # Parse results
            jobs_data = response_data.get('results', [])
            total_results = response_data.get('count', 0)

            logger.info(f"📊 Found {total_results} total jobs, returning {len(jobs_data)}")

            # Convert to JobPosting objects
            jobs = []
            for job_data in jobs_data:
                try:
                    job = self._parse_job(job_data)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Failed to parse job: {e}")
                    continue

            # Cache the results
            self._save_to_cache(cache_key, jobs)

            logger.info(f"✅ Successfully fetched {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"❌ Job search failed: {e}")
            raise

    def get_categories(self) -> List[str]:
        """Get available job categories from Adzuna"""
        try:
            endpoint = f"jobs/{self.country}/categories"
            response_data = self._make_request(endpoint, {})
            categories = response_data.get('results', [])
            return [cat.get('label') for cat in categories if cat.get('label')]
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return []


# Convenience function
def search_jobs(query: str, location: str = "", results_per_page: int = 50) -> List[JobPosting]:
    """
    Convenience function to search for jobs

    Args:
        query: Job search query
        location: Location to search in
        results_per_page: Number of results (max 50)

    Returns:
        List of JobPosting objects
    """
    fetcher = JobFetcher()
    return fetcher.search_jobs(query, location, results_per_page)
