"""
Pydantic models for structured data representation
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated
from datetime import date
from enum import Enum


# ===================================
# Custom Type for Handling None Lists
# ===================================

def none_to_list(v):
    """Convert None to empty list for LLM responses"""
    return v if v is not None else []

# Custom type that accepts None and converts to empty list
ListOrNone = Annotated[List, BeforeValidator(none_to_list)]


# ===================================
# Enums for Controlled Values
# ===================================

class EducationLevel(str, Enum):
    """Education level enumeration"""
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate Degree"
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    PHD = "PhD"
    OTHER = "Other"


class CareerLevel(str, Enum):
    """Career seniority level"""
    INTERN = "Intern"
    JUNIOR = "Junior"
    MID = "Mid-Level"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"
    EXECUTIVE = "Executive"


class RemotePreference(str, Enum):
    """Remote work preference"""
    ONSITE = "On-site"
    HYBRID = "Hybrid"
    REMOTE = "Remote"
    FLEXIBLE = "Flexible"


class ContractType(str, Enum):
    """Employment contract type"""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"
    OTHER = "Other"


# ===================================
# Nested Models
# ===================================

class WorkExperience(BaseModel):
    """Individual work experience entry"""
    company_name: str = Field(description="Name of the company")
    job_title: str = Field(description="Job title/position held")
    duration: str = Field(description="Duration of employment (e.g., '2 years' or 'Jan 2020 - Dec 2022')")
    industry: str = Field(description="Industry sector (e.g., 'Technology', 'Finance')")
    responsibilities: Optional[List[str]] = Field(
        default=None,
        description="Key responsibilities or achievements"
    )


class Education(BaseModel):
    """Educational background entry"""
    level: EducationLevel = Field(description="Highest level of education")
    field_of_study: Optional[str] = Field(
        default=None,
        description="Major or field of study"
    )
    institution: Optional[str] = Field(
        default=None,
        description="Name of educational institution"
    )
    graduation_year: Optional[int] = Field(
        default=None,
        description="Year of graduation"
    )


class Certification(BaseModel):
    """Professional certification"""
    name: str = Field(description="Certification name")
    issuing_organization: Optional[str] = Field(
        default=None,
        description="Organization that issued the certification"
    )
    issue_date: Optional[str] = Field(
        default=None,
        description="When the certification was obtained"
    )


class ExternalLinks(BaseModel):
    """External profile links"""
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: Optional[List[str]] = None


# ===================================
# Main Resume Model
# ===================================

class Resume(BaseModel):
    """Complete structured resume data"""

    # Personal Information (Session only - not persisted)
    name: Optional[str] = Field(default=None, description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Contact email")
    external_links: Optional[ExternalLinks] = Field(
        default=None,
        description="LinkedIn, GitHub, portfolio links"
    )

    # Core Matching Fields
    target_job_titles: ListOrNone[str] = Field(
        default=[],
        description="Job titles the candidate is seeking"
    )

    current_location: Optional[str] = Field(
        default=None,
        description="Current city/region"
    )

    desired_job_location: Optional[str] = Field(
        default=None,
        description="Preferred job location"
    )

    remote_preference: Optional[RemotePreference] = Field(
        default=None,
        description="Remote work preference"
    )

    career_level: Optional[CareerLevel] = Field(
        default=None,
        description="Career seniority level"
    )

    years_of_experience: Optional[int] = Field(
        default=None,
        description="Total years of work experience",
        ge=0
    )

    # Work History
    work_experience: ListOrNone[WorkExperience] = Field(
        default=[],
        description="List of previous work experiences"
    )

    past_industries: ListOrNone[str] = Field(
        default=[],
        description="Industries worked in"
    )

    # Education
    education: ListOrNone[Education] = Field(
        default=[],
        description="Educational background"
    )

    # Skills
    technical_skills: ListOrNone[str] = Field(
        default=[],
        description="Technical skills and tools"
    )

    soft_skills: ListOrNone[str] = Field(
        default=[],
        description="Soft skills (leadership, communication, etc.)"
    )

    languages: ListOrNone[str] = Field(
        default=[],
        description="Spoken languages"
    )

    # Certifications
    certifications: ListOrNone[Certification] = Field(
        default=[],
        description="Professional certifications"
    )

    # Raw text for embedding later
    raw_text: Optional[str] = Field(
        default=None,
        description="Full extracted text from PDF"
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "target_job_titles": ["Senior Software Engineer", "Tech Lead"],
                "current_location": "San Francisco, CA",
                "desired_job_location": "Remote or San Francisco",
                "remote_preference": "Hybrid",
                "career_level": "Senior",
                "years_of_experience": 8,
                "technical_skills": ["Python", "Docker", "AWS", "PostgreSQL"],
                "soft_skills": ["Leadership", "Communication", "Problem Solving"],
                "languages": ["English", "Spanish"]
            }
        }


# ===================================
# Job Posting Model
# ===================================

class JobPosting(BaseModel):
    """Job posting from Adzuna API"""

    # Core Job Information
    job_title: str = Field(description="Job title/position")
    company_name: str = Field(description="Company/employer name")
    description: str = Field(description="Full job description text")
    location: str = Field(description="Job location (city, region, country)")

    # URLs
    job_url: str = Field(description="Adzuna job listing URL")
    redirect_url: Optional[str] = Field(
        default=None,
        description="Direct application URL (company website)"
    )

    # Job Details
    posted_date: Optional[date] = Field(
        default=None,
        description="Date the job was posted"
    )
    contract_type: Optional[ContractType] = Field(
        default=None,
        description="Employment contract type"
    )
    category: Optional[str] = Field(
        default=None,
        description="Job category/industry sector"
    )

    # Salary (often not available)
    salary_min: Optional[float] = Field(
        default=None,
        description="Minimum salary",
        ge=0
    )
    salary_max: Optional[float] = Field(
        default=None,
        description="Maximum salary",
        ge=0
    )
    salary_currency: Optional[str] = Field(
        default=None,
        description="Salary currency (e.g., EUR, USD)"
    )

    # Matching Fields (populated by matching engine)
    match_score: Optional[float] = Field(
        default=None,
        description="Match percentage (0-100)",
        ge=0,
        le=100
    )
    match_explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why this job matches"
    )
    required_skills: Optional[List[str]] = Field(
        default=None,
        description="Skills extracted from job description"
    )

    # Metadata
    adzuna_job_id: Optional[str] = Field(
        default=None,
        description="Adzuna's unique job identifier"
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "job_title": "Senior Data Scientist",
                "company_name": "TechCorp",
                "description": "We are looking for an experienced Data Scientist...",
                "location": "Brussels, Belgium",
                "job_url": "https://www.adzuna.be/details/123456",
                "redirect_url": "https://techcorp.com/careers/apply/123",
                "posted_date": "2024-10-01",
                "contract_type": "Full-time",
                "category": "IT & Technology",
                "salary_min": 60000,
                "salary_max": 80000,
                "salary_currency": "EUR",
                "match_score": 87.5,
                "match_explanation": "Strong match based on Python and ML skills",
                "required_skills": ["Python", "Machine Learning", "SQL"]
            }
        }
