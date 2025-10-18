"""
Test script for JobFetcher
"""
import sys
from app.job_fetcher import JobFetcher
from app.config import settings


def main():
    # Get search parameters from command line or use defaults
    if len(sys.argv) >= 2:
        query = sys.argv[1]
    else:
        query = "Data Scientist"

    if len(sys.argv) >= 3:
        location = sys.argv[2]
    else:
        location = "Belgium"

    if len(sys.argv) >= 4:
        try:
            results_per_page = int(sys.argv[3])
        except ValueError:
            results_per_page = 10
    else:
        results_per_page = 10

    print("=" * 60)
    print("🔍 JOB FETCHER TEST")
    print("=" * 60)

    # Check API credentials
    print("\n🔑 Checking API Credentials...")
    print("-" * 60)
    api_status = settings.validate_api_keys()

    if not api_status['adzuna']:
        print("❌ Error: Adzuna credentials not found!")
        print("Please set ADZUNA_APP_ID and ADZUNA_API_KEY in your .env file")
        sys.exit(1)
    else:
        print("✅ Adzuna credentials: Configured")

    # Check cache status
    if settings.enable_cache:
        print(f"✅ Redis cache: Enabled (TTL={settings.cache_ttl}s)")
    else:
        print("⚠️  Redis cache: Disabled")

    print("-" * 60)

    # Display search parameters
    print(f"\n📋 Search Parameters:")
    print(f"   Query: '{query}'")
    print(f"   Location: '{location}'")
    print(f"   Results: {results_per_page}")
    print(f"   Country: {settings.adzuna_country}")

    try:
        # Initialize fetcher
        print(f"\n🔧 Initializing JobFetcher...")
        fetcher = JobFetcher()

        # Search for jobs
        print(f"\n🌐 Fetching jobs from Adzuna API...")
        jobs = fetcher.search_jobs(
            query=query,
            location=location,
            results_per_page=results_per_page
        )

        # Display results
        print("\n" + "=" * 60)
        print(f"✅ FOUND {len(jobs)} JOBS")
        print("=" * 60)

        for i, job in enumerate(jobs, 1):
            print(f"\n📌 Job #{i}")
            print("-" * 60)
            print(f"Title: {job.job_title}")
            print(f"Company: {job.company_name}")
            print(f"Location: {job.location}")

            if job.contract_type:
                print(f"Contract: {job.contract_type}")

            if job.category:
                print(f"Category: {job.category}")

            if job.salary_min or job.salary_max:
                salary_str = ""
                if job.salary_min and job.salary_max:
                    salary_str = f"{job.salary_currency} {job.salary_min:,.0f} - {job.salary_max:,.0f}"
                elif job.salary_min:
                    salary_str = f"{job.salary_currency} {job.salary_min:,.0f}+"
                elif job.salary_max:
                    salary_str = f"Up to {job.salary_currency} {job.salary_max:,.0f}"
                print(f"Salary: {salary_str}")

            if job.posted_date:
                print(f"Posted: {job.posted_date}")

            # Show first 200 chars of description
            desc_preview = job.description[:200].replace('\n', ' ')
            print(f"\nDescription: {desc_preview}...")

            print(f"\n🔗 URL: {job.job_url}")

        # Test caching
        print("\n" + "=" * 60)
        print("🧪 TESTING CACHE")
        print("=" * 60)
        print("\nSearching again with same parameters (should use cache)...")

        jobs_cached = fetcher.search_jobs(
            query=query,
            location=location,
            results_per_page=results_per_page
        )

        if len(jobs_cached) == len(jobs):
            print(f"✅ Cache working! Retrieved {len(jobs_cached)} jobs from cache")
        else:
            print(f"⚠️  Cache may not be working correctly")

        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        companies = set(job.company_name for job in jobs)
        locations = set(job.location for job in jobs)
        categories = set(job.category for job in jobs if job.category)

        print(f"Total jobs found: {len(jobs)}")
        print(f"Unique companies: {len(companies)}")
        print(f"Unique locations: {len(locations)}")
        print(f"Job categories: {len(categories)}")

        if categories:
            print(f"\nCategories found:")
            for cat in sorted(categories):
                print(f"  • {cat}")

        # Option to show all jobs
        print("\n" + "=" * 60)
        show_all = input("\n📄 Show full details for all jobs? (y/n): ").lower()

        if show_all == 'y':
            for i, job in enumerate(jobs, 1):
                print("\n" + "=" * 60)
                print(f"JOB #{i} - FULL DETAILS")
                print("=" * 60)
                print(f"\nTitle: {job.job_title}")
                print(f"Company: {job.company_name}")
                print(f"Location: {job.location}")
                print(f"Category: {job.category or 'N/A'}")
                print(f"Contract: {job.contract_type or 'N/A'}")
                print(f"Posted: {job.posted_date or 'N/A'}")
                print(f"\nFull Description:\n{job.description}")
                print(f"\nApply at: {job.job_url}")
                print(f"Redirect URL: {job.redirect_url or 'N/A'}")
                input("\nPress Enter for next job...")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n💡 Usage: python test_job_fetcher.py [query] [location] [num_results]")
    print("   Example: python test_job_fetcher.py 'Data Scientist' 'Belgium' 20")
    print("   Default: python test_job_fetcher.py 'Data Scientist' 'Belgium' 10\n")

    main()
