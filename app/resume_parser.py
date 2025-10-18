"""
Resume Parser - Extract and structure resume data from PDF
"""
from pathlib import Path
from typing import Optional
import pypdf
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from app.models import Resume
from app.config import settings
from loguru import logger


class ResumeParser:
    """Parse PDF resumes and extract structured data using LLM"""

    def __init__(self):
        """Initialize the parser with LLM"""
        self.llm = self._setup_llm()
        self.extraction_chain = self._create_extraction_chain()
        logger.info(f"ResumeParser initialized with model: {settings.llm_model}")

    def _setup_llm(self):
        """Set up the LLM based on configuration"""
        if settings.has_openai_key:
            logger.info("Using OpenAI LLM")
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key
            )
        elif settings.has_anthropic_key:
            logger.info("Using Anthropic Claude LLM")
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(
                "No LLM API key found! Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
            )

    def _create_extraction_chain(self):
        """Create LangChain extraction chain with structured output"""

        # Define the extraction prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume parser. Extract structured information from the resume text.

            Instructions:
            - Extract all relevant information accurately
            - If a field is not present, leave it as null/empty
            - For target_job_titles: infer from recent positions or objective statement
            - For career_level: infer from years of experience and job titles
            - For years_of_experience: calculate total years across all positions
            - Standardize industry names (e.g., "Tech" → "Technology")
            - Extract technical skills, soft skills, and languages separately
            - Parse work experience with company, title, duration, and industry
            - Be thorough but accurate - don't hallucinate information
            """),
            ("human", "Resume text:\n\n{resume_text}")
        ])

        # Create chain with structured output
        structured_llm = self.llm.with_structured_output(Resume)
        chain = prompt | structured_llm

        return chain

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as string
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")

        logger.info(f"Extracting text from: {path.name}")

        try:
            # Extract text using PyPDF
            reader = pypdf.PdfReader(str(path))
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(page_text)
                    logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")

            full_text = "\n\n".join(text_parts)

            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")

            logger.info(f"Successfully extracted {len(full_text)} characters")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    def structure_data(self, text: str) -> Resume:
        """
        Use LLM to extract structured data from resume text

        Args:
            text: Raw resume text

        Returns:
            Structured Resume object
        """
        logger.info("Structuring resume data with LLM...")

        try:
            # Invoke the extraction chain
            resume = self.extraction_chain.invoke({"resume_text": text})

            # Add raw text to the resume object
            resume.raw_text = text

            logger.info(f"Successfully structured resume for: {resume.name or 'Unknown'}")
            logger.debug(f"Extracted {len(resume.technical_skills)} technical skills")
            logger.debug(f"Extracted {len(resume.work_experience)} work experiences")

            return resume

        except Exception as e:
            logger.error(f"Error structuring resume data: {e}")
            raise

    def parse(self, pdf_path: str) -> Resume:
        """
        Main method: Parse PDF resume and return structured data

        Args:
            pdf_path: Path to the PDF resume file

        Returns:
            Structured Resume object
        """
        logger.info(f"Starting resume parsing: {pdf_path}")

        try:
            # Step 1: Extract text from PDF
            text = self.extract_text(pdf_path)

            # Step 2: Structure the data using LLM
            resume = self.structure_data(text)

            logger.info("✅ Resume parsing completed successfully")
            return resume

        except Exception as e:
            logger.error(f"❌ Resume parsing failed: {e}")
            raise

    def parse_from_text(self, text: str) -> Resume:
        """
        Parse resume from already extracted text (useful for testing)

        Args:
            text: Resume text

        Returns:
            Structured Resume object
        """
        return self.structure_data(text)


# Convenience function for simple usage
def parse_resume(pdf_path: str) -> Resume:
    """
    Convenience function to parse a resume PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Structured Resume object
    """
    parser = ResumeParser()
    return parser.parse(pdf_path)
