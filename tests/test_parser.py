"""
Test script for ResumeParser
"""
import sys
from pathlib import Path
from app.resume_parser import ResumeParser
from app.config import settings
import json


def main():
    # Check if PDF path provided
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <path_to_resume.pdf>")
        print("\nExample: python test_parser.py ./data/resumes/my_resume.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Validate API keys
    print("🔑 Checking API Keys...")
    print("-" * 50)
    api_status = settings.validate_api_keys()
    for service, status in api_status.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.capitalize()}: {'Configured' if status else 'Missing'}")
    print("-" * 50)

    if not settings.has_openai_key and not settings.has_anthropic_key:
        print("\n❌ Error: No LLM API key found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        sys.exit(1)

    print(f"\n📄 Testing Resume Parser with: {pdf_path}\n")

    try:
        # Initialize parser
        print("🔧 Initializing parser...")
        parser = ResumeParser()

        # Parse the resume
        print("📖 Extracting text from PDF...")
        resume = parser.parse(pdf_path)

        # Display results
        print("\n" + "=" * 50)
        print("✅ PARSING SUCCESSFUL!")
        print("=" * 50)

        print(f"\n👤 Personal Information:")
        print(f"   Name: {resume.name or 'Not found'}")
        print(f"   Email: {resume.email or 'Not found'}")
        print(f"   Location: {resume.current_location or 'Not found'}")

        print(f"\n🎯 Career Profile:")
        print(f"   Target Roles: {', '.join(resume.target_job_titles) if resume.target_job_titles else 'Not specified'}")
        print(f"   Career Level: {resume.career_level or 'Not determined'}")
        print(f"   Years of Experience: {resume.years_of_experience or 'Not specified'}")
        print(f"   Remote Preference: {resume.remote_preference or 'Not specified'}")

        print(f"\n💼 Work Experience ({len(resume.work_experience)} positions):")
        for i, exp in enumerate(resume.work_experience, 1):
            print(f"   {i}. {exp.job_title} at {exp.company_name}")
            print(f"      Duration: {exp.duration} | Industry: {exp.industry}")

        print(f"\n🎓 Education ({len(resume.education)} entries):")
        for edu in resume.education:
            print(f"   • {edu.level}", end="")
            if edu.field_of_study:
                print(f" in {edu.field_of_study}", end="")
            if edu.institution:
                print(f" - {edu.institution}", end="")
            print()

        print(f"\n💻 Technical Skills ({len(resume.technical_skills)}):")
        if resume.technical_skills:
            # Display in rows of 5
            for i in range(0, len(resume.technical_skills), 5):
                skills_row = resume.technical_skills[i:i+5]
                print(f"   {', '.join(skills_row)}")
        else:
            print("   None found")

        print(f"\n🤝 Soft Skills ({len(resume.soft_skills)}):")
        print(f"   {', '.join(resume.soft_skills) if resume.soft_skills else 'None found'}")

        print(f"\n🌍 Languages ({len(resume.languages)}):")
        print(f"   {', '.join(resume.languages) if resume.languages else 'None found'}")

        print(f"\n🏆 Certifications ({len(resume.certifications)}):")
        for cert in resume.certifications:
            print(f"   • {cert.name}", end="")
            if cert.issuing_organization:
                print(f" ({cert.issuing_organization})", end="")
            print()

        if resume.external_links:
            print(f"\n🔗 External Links:")
            if resume.external_links.linkedin:
                print(f"   LinkedIn: {resume.external_links.linkedin}")
            if resume.external_links.github:
                print(f"   GitHub: {resume.external_links.github}")
            if resume.external_links.portfolio:
                print(f"   Portfolio: {resume.external_links.portfolio}")

        # Option to save as JSON
        print("\n" + "=" * 50)
        save = input("\n💾 Save parsed data as JSON? (y/n): ").lower()
        if save == 'y':
            output_path = Path(pdf_path).stem + "_parsed.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resume.model_dump(mode='json'), f, indent=2, default=str)
            print(f"✅ Saved to: {output_path}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
