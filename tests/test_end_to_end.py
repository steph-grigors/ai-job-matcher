"""
End-to-End Test: Resume Parser → Job Fetcher → Matcher
"""
import sys
from pathlib import Path
from app.resume_parser import ResumeParser
from app.job_fetcher import JobFetcher
from app.matcher import JobMatcher
from app.config import settings


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    print(f"\n{char * 70}")
    print(f"{title}")
    print(f"{char * 70}")


def main():
    # Get parameters
    if len(sys.argv) < 2:
        print("Usage: python test_end_to_end.py <resume.pdf> [query] [location] [num_jobs]")
        print("\nExample:")
        print("  python test_end_to_end.py 'data/resumes/resume.pdf' 'Data Scientist' 'Sydney' 20")
        sys.exit(1)

    resume_path = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) >= 3 else None  # Will use resume targets if None
    location = sys.argv[3] if len(sys.argv) >= 4 else "Sydney"
    num_jobs = int(sys.argv[4]) if len(sys.argv) >= 5 else 20

    print_section("🚀 AI JOB MATCHER - END-TO-END TEST")

    # Validate API keys
    print("\n🔑 Checking API Keys...")
    api_status = settings.validate_api_keys()
    for service, status in api_status.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {service.capitalize()}: {'Configured' if status else 'Missing'}")

    if not api_status['openai'] and not api_status['anthropic']:
        print("\n❌ Error: LLM API key required!")
        sys.exit(1)
    if not api_status['adzuna']:
        print("\n❌ Error: Adzuna API key required!")
        sys.exit(1)

    try:
        # ====================================
        # STEP 1: Parse Resume
        # ====================================
        print_section("📄 STEP 1: PARSING RESUME", "-")
        print(f"Resume: {resume_path}")

        parser = ResumeParser()
        resume = parser.parse(resume_path)

        print(f"\n✅ Resume parsed successfully!")
        print(f"   Name: {resume.name or 'Not found'}")
        print(f"   Target Roles: {', '.join(resume.target_job_titles[:3]) if resume.target_job_titles else 'None'}")
        print(f"   Career Level: {resume.career_level or 'Not specified'}")
        print(f"   Years of Experience: {resume.years_of_experience or 'Not specified'}")
        print(f"   Technical Skills: {len(resume.technical_skills)} found")
        print(f"   Work Experience: {len(resume.work_experience)} positions")

        # Determine search query
        if not query and resume.target_job_titles:
            query = resume.target_job_titles[0]
            print(f"\n💡 Using first target role as search query: '{query}'")
        elif not query:
            print("\n❌ Error: No query specified and no target roles in resume!")
            sys.exit(1)

        # ====================================
        # STEP 2: Fetch Jobs
        # ====================================
        print_section("🔍 STEP 2: FETCHING JOBS", "-")
        print(f"Query: '{query}'")
        print(f"Location: '{location}'")
        print(f"Requesting: {num_jobs} jobs")

        fetcher = JobFetcher()
        jobs = fetcher.search_jobs(
            query=query,
            location=location,
            results_per_page=min(num_jobs, 50)  # Adzuna max is 50
        )

        print(f"\n✅ Found {len(jobs)} jobs")
        if len(jobs) > 0:
            print(f"\nSample jobs:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"   {i}. {job.job_title} at {job.company_name}")

        if len(jobs) == 0:
            print("\n⚠️  No jobs found. Try different search parameters.")
            sys.exit(0)

        # ====================================
        # STEP 3: Match Jobs
        # ====================================
        print_section("🎯 STEP 3: MATCHING JOBS", "-")
        print(f"Matching resume against {len(jobs)} jobs...")
        print(f"LLM scoring enabled: {settings.use_llm_scoring}")
        print(f"Top jobs for LLM scoring: {settings.top_n_matches}")

        matcher = JobMatcher()
        matched_jobs = matcher.match_jobs(
            resume=resume,
            jobs=jobs,
            top_n_for_llm=settings.top_n_matches
        )

        print(f"\n✅ Matching complete!")

        # ====================================
        # STEP 4: Display Results
        # ====================================
        print_section("🏆 TOP MATCHES")

        # Show top 10 matches
        top_matches = matched_jobs[:10]

        for i, job in enumerate(top_matches, 1):
            print(f"\n{'=' * 70}")
            print(f"🥇 RANK #{i} - Match Score: {job.match_score}%")
            print(f"{'=' * 70}")
            print(f"Title: {job.job_title}")
            print(f"Company: {job.company_name}")
            print(f"Location: {job.location}")

            if job.contract_type:
                print(f"Contract: {job.contract_type}")

            if job.category:
                print(f"Category: {job.category}")

            if job.salary_min or job.salary_max:
                if job.salary_min and job.salary_max:
                    print(f"Salary: {job.salary_currency} {job.salary_min:,.0f} - {job.salary_max:,.0f}")
                elif job.salary_min:
                    print(f"Salary: {job.salary_currency} {job.salary_min:,.0f}+")

            if job.posted_date:
                print(f"Posted: {job.posted_date}")

            # Show match explanation if available
            if job.match_explanation:
                print(f"\n📝 Match Analysis:")
                print(f"{job.match_explanation}")

            # Show description preview
            desc_preview = job.description[:300].replace('\n', ' ').strip()
            print(f"\n📄 Description Preview:")
            print(f"{desc_preview}...")

            print(f"\n🔗 Apply: {job.job_url}")

        # ====================================
        # Summary Statistics
        # ====================================
        print_section("📊 SUMMARY STATISTICS")

        # Calculate statistics
        avg_score = sum(j.match_score for j in matched_jobs if j.match_score) / len(matched_jobs)
        high_matches = [j for j in matched_jobs if j.match_score and j.match_score >= 70]
        medium_matches = [j for j in matched_jobs if j.match_score and 50 <= j.match_score < 70]
        low_matches = [j for j in matched_jobs if j.match_score and j.match_score < 50]

        print(f"\nTotal jobs analyzed: {len(matched_jobs)}")
        print(f"Average match score: {avg_score:.1f}%")
        print(f"\nMatch Distribution:")
        print(f"   🟢 High matches (70-100%): {len(high_matches)}")
        print(f"   🟡 Medium matches (50-69%): {len(medium_matches)}")
        print(f"   🔴 Low matches (0-49%): {len(low_matches)}")

        # Top companies
        companies = {}
        for job in matched_jobs[:10]:
            companies[job.company_name] = companies.get(job.company_name, 0) + 1

        if companies:
            print(f"\nTop companies in results:")
            for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {company}: {count} job(s)")

        # ====================================
        # Interactive Options
        # ====================================
        print_section("💾 SAVE RESULTS?")

        save = input("\nSave results to JSON file? (y/n): ").lower()
        if save == 'y':
            import json
            from datetime import datetime

            output_file = f"match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            results = {
                "resume": {
                    "name": resume.name,
                    "target_roles": resume.target_job_titles,
                    "career_level": resume.career_level,
                    "years_of_experience": resume.years_of_experience,
                    "technical_skills": resume.technical_skills,
                },
                "search_params": {
                    "query": query,
                    "location": location,
                    "num_jobs": num_jobs
                },
                "matches": [
                    {
                        "rank": i + 1,
                        "match_score": job.match_score,
                        "job_title": job.job_title,
                        "company": job.company_name,
                        "location": job.location,
                        "url": job.job_url,
                        "explanation": job.match_explanation
                    }
                    for i, job in enumerate(matched_jobs)
                ]
            }

            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"✅ Results saved to: {output_file}")

        print_section("✨ TEST COMPLETE!")
        print("\n🎉 All components working successfully!")
        print("   ✅ Resume Parser")
        print("   ✅ Job Fetcher")
        print("   ✅ Matching Engine")
        print("\nYou're ready to build the Streamlit UI! 🚀")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
