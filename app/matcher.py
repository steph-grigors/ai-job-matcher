"""
Matching Engine - Match resumes with job postings using embeddings and LLM
"""
from typing import List, Tuple
import numpy as np
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import faiss
from loguru import logger

from app.models import Resume, JobPosting
from app.config import settings


class JobMatcher:
    """Match resumes with job postings using semantic similarity and LLM scoring"""

    def __init__(self):
        """Initialize the matcher with embeddings model and LLM"""
        self.embeddings = self._setup_embeddings()
        self.llm = self._setup_llm()
        logger.info("JobMatcher initialized")

    def _setup_embeddings(self):
        """Setup embeddings model"""
        if settings.has_openai_key:
            logger.info(f"Using OpenAI embeddings: {settings.embedding_model}")
            return OpenAIEmbeddings(
                model=settings.embedding_model,
                api_key=settings.openai_api_key
            )
        else:
            raise ValueError(
                "OpenAI API key required for embeddings. "
                "Please set OPENAI_API_KEY in .env"
            )

    def _setup_llm(self):
        """Setup LLM for detailed scoring"""
        if settings.has_openai_key:
            logger.info(f"Using OpenAI LLM: {settings.llm_model}")
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key
            )
        elif settings.has_anthropic_key:
            logger.info(f"Using Anthropic Claude: {settings.llm_model}")
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(
                "LLM API key required. "
                "Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
            )

    def _create_resume_text(self, resume: Resume) -> str:
        """
        Create a focused text representation of resume for embedding
        Includes: skills + work experience summary
        """
        parts = []

        # Add target job titles
        if resume.target_job_titles:
            parts.append(f"Target roles: {', '.join(resume.target_job_titles)}")

        # Add technical skills
        if resume.technical_skills:
            parts.append(f"Technical skills: {', '.join(resume.technical_skills)}")

        # Add soft skills
        if resume.soft_skills:
            parts.append(f"Soft skills: {', '.join(resume.soft_skills)}")

        # Add work experience summaries
        if resume.work_experience:
            exp_summaries = []
            for exp in resume.work_experience:
                exp_text = f"{exp.job_title} at {exp.company_name} ({exp.duration}) in {exp.industry}"
                if exp.responsibilities:
                    # Take first 2 responsibilities
                    resp = '. '.join(exp.responsibilities[:2])
                    exp_text += f". {resp}"
                exp_summaries.append(exp_text)
            parts.append("Work experience:\n" + "\n".join(exp_summaries))

        # Add career level and years of experience
        if resume.career_level:
            parts.append(f"Career level: {resume.career_level}")
        if resume.years_of_experience:
            parts.append(f"Years of experience: {resume.years_of_experience}")

        return "\n\n".join(parts)

    def _calculate_similarity_scores(
        self,
        resume_embedding: List[float],
        job_embeddings: List[List[float]]
    ) -> List[float]:
        """
        Calculate cosine similarity between resume and jobs using FAISS

        Args:
            resume_embedding: Resume embedding vector
            job_embeddings: List of job embedding vectors

        Returns:
            List of similarity scores (0-1)
        """
        # Convert to numpy arrays
        resume_vec = np.array([resume_embedding], dtype=np.float32)
        job_vecs = np.array(job_embeddings, dtype=np.float32)

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(resume_vec)
        faiss.normalize_L2(job_vecs)

        # Create FAISS index
        dimension = len(resume_embedding)
        index = faiss.IndexFlatIP(dimension)  # Inner Product = cosine similarity after normalization
        index.add(job_vecs)

        # Search
        similarities, _ = index.search(resume_vec, len(job_embeddings))

        return similarities[0].tolist()

    def _score_job_with_llm(self, resume: Resume, job: JobPosting) -> Tuple[float, str]:
        """
        Use LLM to score a single job match and generate explanation

        Args:
            resume: Resume object
            job: JobPosting object

        Returns:
            Tuple of (score 0-100, explanation)
        """
        # Create prompt for LLM scoring
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert recruiter evaluating job-candidate matches.

Your task:
1. Analyze how well the candidate's profile matches the job requirements
2. Provide a match score from 0-100 where:
   - 90-100: Excellent match, highly qualified
   - 70-89: Good match, meets most requirements
   - 50-69: Moderate match, meets some requirements
   - 30-49: Weak match, missing key requirements
   - 0-29: Poor match, not qualified

3. Provide a concise explanation (2-3 sentences) covering:
   - Key strengths/alignments
   - Any gaps or mismatches
   - Overall recommendation

Be honest and objective. Consider skills, experience level, industry fit, and job requirements.

Respond in this exact format:
SCORE: [number 0-100]
EXPLANATION: [your 2-3 sentence explanation]
"""),
            ("human", """Candidate Profile:
Name: {name}
Target Roles: {target_roles}
Career Level: {career_level}
Years of Experience: {years_exp}
Technical Skills: {tech_skills}
Soft Skills: {soft_skills}
Work Experience: {work_exp}

Job Posting:
Title: {job_title}
Company: {company}
Location: {location}
Description: {job_description}

Evaluate this match.""")
        ])

        # Prepare resume data
        resume_data = {
            "name": resume.name or "Unknown",
            "target_roles": ", ".join(resume.target_job_titles) if resume.target_job_titles else "Not specified",
            "career_level": resume.career_level or "Not specified",
            "years_exp": resume.years_of_experience or "Not specified",
            "tech_skills": ", ".join(resume.technical_skills) if resume.technical_skills else "None listed",
            "soft_skills": ", ".join(resume.soft_skills) if resume.soft_skills else "None listed",
            "work_exp": "\n".join([
                f"- {exp.job_title} at {exp.company_name} ({exp.duration})"
                for exp in resume.work_experience[:3]  # Top 3 experiences
            ]) if resume.work_experience else "No work experience listed",
            "job_title": job.job_title,
            "company": job.company_name,
            "location": job.location,
            "job_description": job.description[:1000]  # Limit description length
        }

        try:
            chain = prompt | self.llm
            response = chain.invoke(resume_data)

            # Parse response
            response_text = response.content

            # Extract score
            score = 0.0
            explanation = "Unable to generate explanation"

            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('SCORE:'):
                    try:
                        score = float(line.split('SCORE:')[1].strip())
                        score = max(0.0, min(100.0, score))  # Clamp to 0-100
                    except ValueError:
                        logger.warning(f"Could not parse score from: {line}")
                elif line.startswith('EXPLANATION:'):
                    explanation = line.split('EXPLANATION:')[1].strip()

            logger.debug(f"LLM scored job '{job.job_title}': {score}%")
            return score, explanation

        except Exception as e:
            logger.error(f"LLM scoring failed for job '{job.job_title}': {e}")
            return 0.0, "Scoring failed"

    def match_jobs(
        self,
        resume: Resume,
        jobs: List[JobPosting],
        top_n_for_llm: int = 10
    ) -> List[JobPosting]:
        """
        Match resume with jobs using embeddings + LLM scoring

        Args:
            resume: Resume object
            jobs: List of JobPosting objects
            top_n_for_llm: Number of top matches to score with LLM

        Returns:
            List of JobPosting objects sorted by match score (highest first)
        """
        if not jobs:
            logger.warning("No jobs to match")
            return []

        logger.info(f"🎯 Matching resume against {len(jobs)} jobs...")

        # Step 1: Create resume text for embedding
        resume_text = self._create_resume_text(resume)
        logger.debug(f"Resume text length: {len(resume_text)} chars")

        # Step 2: Generate embeddings
        logger.info("🔢 Generating embeddings...")
        resume_embedding = self.embeddings.embed_query(resume_text)

        job_texts = [job.description for job in jobs]
        job_embeddings = self.embeddings.embed_documents(job_texts)

        logger.info(f"✅ Generated {len(job_embeddings)} job embeddings")

        # Step 3: Calculate similarity scores
        logger.info("📊 Calculating similarity scores...")
        similarity_scores = self._calculate_similarity_scores(resume_embedding, job_embeddings)

        # Add similarity scores to jobs
        for job, similarity in zip(jobs, similarity_scores):
            # Convert to percentage and store as match_score temporarily
            job.match_score = round(similarity * 100, 2)

        # Step 4: Rank by similarity
        jobs_ranked = sorted(jobs, key=lambda j: j.match_score, reverse=True)

        logger.info(f"Top 3 similarity scores: {[j.match_score for j in jobs_ranked[:3]]}")

        # Step 5: LLM scoring for top N
        if settings.use_llm_scoring:
            logger.info(f"🤖 LLM scoring top {top_n_for_llm} jobs...")

            for i, job in enumerate(jobs_ranked[:top_n_for_llm]):
                logger.info(f"Scoring job {i+1}/{top_n_for_llm}: {job.job_title}")
                llm_score, explanation = self._score_job_with_llm(resume, job)

                # Store both scores separately
                similarity_score = job.match_score  # Save the similarity score
                job.match_score = llm_score  # Replace with LLM score
                job.match_explanation = explanation

                # Add similarity info to explanation
                job.match_explanation = (
                    f"[Similarity: {similarity_score}% | LLM Score: {llm_score}%]\n\n"
                    f"{explanation}"
                )

            # Re-rank by LLM scores
            jobs_ranked = sorted(jobs_ranked, key=lambda j: j.match_score or 0, reverse=True)

            logger.info("✅ LLM scoring complete")

        logger.info(f"🎉 Matching complete! Top match: {jobs_ranked[0].job_title} ({jobs_ranked[0].match_score}%)")

        return jobs_ranked


# Convenience function
def match_resume_to_jobs(
    resume: Resume,
    jobs: List[JobPosting],
    top_n_for_llm: int = 10
) -> List[JobPosting]:
    """
    Convenience function to match resume to jobs

    Args:
        resume: Resume object
        jobs: List of JobPosting objects
        top_n_for_llm: Number of top jobs to score with LLM

    Returns:
        Sorted list of jobs with match scores
    """
    matcher = JobMatcher()
    return matcher.match_jobs(resume, jobs, top_n_for_llm)
