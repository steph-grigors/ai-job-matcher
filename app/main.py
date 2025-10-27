"""
Streamlit UI for AI Job Matcher
"""
import streamlit as st
from pathlib import Path
import time
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.resume_parser import ResumeParser
from app.job_fetcher import JobFetcher
from app.matcher import JobMatcher
from app.config import settings
from app.country_detector import CountryDetector
from app.ip_tracker import get_query_status_message, can_use_app, use_demo_query, has_user_api_key, get_client_ip


# Page configuration
st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded"
)

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         font-weight: bold;
#         text-align: center;
#         margin-bottom: 2rem;
#         color: #1f77b4;
#     }
#     .sub-header {
#         font-size: 1.5rem;
#         color: #555;
#         text-align: center;
#         margin-bottom: 3rem;
#     }
#     .job-card {
#         background-color: #f8f9fa;
#         padding: 1.5rem;
#         border-radius: 10px;
#         border-left: 5px solid #1f77b4;
#         margin-bottom: 1rem;
#     }
#     .match-score-high {
#         color: #28a745;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .match-score-medium {
#         color: #ffc107;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .match-score-low {
#         color: #dc3545;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .stButton>button {
#         width: 100%;
#     }
#     .job-title {
#         font-size: 1.3rem;
#         font-weight: 600;
#         color: #1f77b4;
#         margin-bottom: 0.5rem;
#     }
#     .rank-badge {
#         display: inline-block;
#         background-color: #e9ecef;
#         padding: 0.2rem 0.6rem;
#         border-radius: 12px;
#         font-size: 0.9rem;
#         font-weight: bold;
#         color: #495057;
#         margin-right: 0.5rem;
#     }
# </style>
# """, unsafe_allow_html=True)


# Initialize session state
if 'resume' not in st.session_state:
    st.session_state.resume = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = None
if 'matched_jobs' not in st.session_state:
    st.session_state.matched_jobs = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = settings.adzuna_country
if 'detected_country' not in st.session_state:
    st.session_state.detected_country = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "upload"
if 'user_openai_key' not in st.session_state:
    st.session_state.user_openai_key = None


def detect_country_from_location():
    """Helper function to detect country from location field"""
    pass  # Detection happens inline in the UI


def about_tab():
    """Tab 4: About the application"""


    # Two-Column Layout
    left_col, right_col = st.columns([3, 2], gap="large")

    # ========================================
    # LEFT COLUMN - Main Content
    # ========================================
    with left_col:
        # What is This?
        st.subheader("💡 What is This?")
        st.write("""
        An intelligent job matching platform that analyzes your resume and automatically
        ranks job opportunities using advanced AI. Combines semantic search with LLM-based
        scoring to find roles that truly fit your profile.
        """)

        st.markdown("---")

        # How It Works (Visual Flow)
        st.subheader("🔄 How It Works")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 2rem;'>📄</div>
                <div style='font-weight: bold;'>Upload</div>
                <div style='font-size: 0.8rem; color: #666;'>Your resume</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 2rem;'>🔍</div>
                <div style='font-weight: bold;'>Search</div>
                <div style='font-size: 0.8rem; color: #666;'>Find jobs</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 2rem;'>🎯</div>
                <div style='font-weight: bold;'>Match</div>
                <div style='font-size: 0.8rem; color: #666;'>AI ranks them</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div style='text-align: center;'>
                <div style='font-size: 2rem;'>🚀</div>
                <div style='font-weight: bold;'>Apply</div>
                <div style='font-size: 0.8rem; color: #666;'>Get hired!</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Key Features (Expandable)
        st.subheader("✨ Key Features")

        with st.expander("📄 Smart Resume Parsing", expanded=False):
            st.write("""
            - AI extracts structured data from any resume format
            - Identifies skills, experience, education automatically
            - Handles various layouts and styles
            """)

        with st.expander("🎯 Two-Stage Matching", expanded=False):
            st.write("""
            **Stage 1:** Vector embeddings for fast semantic search (FAISS)

            **Stage 2:** GPT-4o-mini provides detailed scoring & explanations

            Result: Fast + Accurate = Best matches in ~30 seconds
            """)

        with st.expander("🌍 Global Job Search", expanded=False):
            st.write("""
            - 20+ countries supported via Adzuna API
            - 200+ cities with smart auto-detection
            - Real-time job listings with salary data
            """)

        with st.expander("💡 Match Explanations", expanded=False):
            st.write("""
            - Percentage scores (0-100%)
            - Detailed reasoning for each match
            - Identifies strengths and gaps
            """)

        st.markdown("---")

        # Cost & Usage
        st.subheader("💰 Cost & Usage")

        cost_col1, cost_col2 = st.columns(2)

        with cost_col1:
            st.markdown("""
            **🆓 Demo Mode**
            - 1 free resume matching/day
            - Full feature access
            - Perfect for testing
            """)

        with cost_col2:
            st.markdown("""
            **🔑 Your API Key**
            - Unlimited queries
            - ~$0.02 per search
            - [Get free key →](https://platform.openai.com/api-keys)
            """)

    # ========================================
    # RIGHT COLUMN - Highlights & Quick Info
    # ========================================
    with right_col:
        # Quick Stats
        st.subheader("📊 Quick Stats")

        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Countries", "20+", help="Adzuna coverage")
            st.metric("Match Time", "~30s", help="Average processing time")

        with metric_col2:
            st.metric("Cities", "200+", help="Auto-detection database")
            st.metric("Accuracy", "85%+", help="Top match quality")

        st.markdown("---")

        # Technology Stack
        st.subheader("🛠️ Tech Stack")

        st.markdown("""
        <div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;'>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>Python</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>LangChain</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>OpenAI</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>FAISS</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>Docker</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>Streamlit</span>
            <span style='background: #1f77b4; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;'>Pydantic</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Quick Links
        st.subheader("🔗 Quick Links")

        link_col1, link_col2 = st.columns(2)

        with link_col1:
            st.link_button("📂 GitHub", "https://github.com/steph-grigors/ai-job-matcher", use_container_width=True)
            st.link_button("📚 Docs", "https://github.com/steph-grigors/ai-job-matcher#readme", use_container_width=True)

        with link_col2:
            st.link_button("💼 Portfolio", "https://www.stephan-gs.work", use_container_width=True)
            st.link_button("🔗 LinkedIn", "https://linkedin.com/in/stéphan-grs", use_container_width=True)

        st.markdown("---")

        # System Status (Small indicator)
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #e8f5e9; border-radius: 10px;'>
            <div style='font-size: 1.5rem;'>✅</div>
            <div style='font-weight: bold; color: #2e7d32;'>All Systems Operational</div>
            <div style='font-size: 0.8rem; color: #666;'>Ready to match your next role!</div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================
    # BOTTOM SECTION - Developer Info
    # ========================================
    st.divider()

    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h3>👨‍💻 Developed by Stéphan Grigorescu</h3>
        <p style='color: #666;'>
            Data Scientist & AI Engineer | Building intelligent solutions with Python & AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Social Links (centered)
    social_col1, social_col2, social_col3, social_col4 = st.columns([1, 1, 1, 1])

    with social_col1:
        st.link_button("🌐 Portfolio", "https://www.stephan-gs.work", use_container_width=True)
    with social_col2:
        st.link_button("💼 LinkedIn", "https://linkedin.com/in/stéphan-grs", use_container_width=True)
    with social_col3:
        st.link_button("🐙 GitHub", "https://github.com/steph-grigors", use_container_width=True)
    with social_col4:
        st.link_button("📧 Contact", "mailto:stephan.grigorescu@gmail.com", use_container_width=True)

    # Disclaimer (Collapsed)
    with st.expander("⚖️ Legal Disclaimer"):
        st.caption("""
        This application is provided as-is for educational and demonstration purposes.
        Job listings are sourced from Adzuna and the accuracy of matches depends on
        the quality of your resume and job descriptions. Always verify job details
        directly with employers. No warranty is provided for the accuracy of AI-generated
        match scores or explanations.
        """)


def main():
    """Main application"""

    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🎯 AI Job Matcher</h1>
        <p style='font-size: 1.2rem; color: #666;'>
            Find your perfect career match with AI-powered intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with info
    with st.sidebar:
        # 1. API Configuration (NEW - Top priority)
        st.header("🔑 API Configuration")

        user_key = st.text_input(
            "OpenAI API Key (Optional)",
            type="password",
            value=st.session_state.user_openai_key or "",
            help="Enter your OpenAI API key for unlimited queries. Leave empty to use demo mode (1 free resume matching per day).",
            placeholder="sk-proj-..."
        )

        # Update session state
        if user_key and user_key != st.session_state.user_openai_key:
            st.session_state.user_openai_key = user_key

        # Show status
        status_message = get_query_status_message()
        if "unlimited" in status_message:
            st.success(status_message)
        elif "exhausted" in status_message:
            st.error(status_message)
        else:
            st.info(status_message)

        if not has_user_api_key():
            st.caption("💡 Get your free API key at [platform.openai.com](https://platform.openai.com/api-keys)")

        st.divider()

        # 2. Settings
        st.header("⚙️ Settings")

        # Country selector with auto-detection
        st.write("**Country Selection**")

        # Show detected country if available
        if st.session_state.detected_country:
            detected_name = CountryDetector.get_country_name(st.session_state.detected_country)
            st.info(f"🔍 Auto-detected: **{detected_name}** ({st.session_state.detected_country.upper()})")

        # Manual country override
        countries = CountryDetector.get_all_countries()
        country_options = {f"{name} ({code.upper()})": code for code, name in countries.items()}

        current_country_display = f"{CountryDetector.get_country_name(st.session_state.selected_country)} ({st.session_state.selected_country.upper()})"

        selected_display = st.selectbox(
            "Override Country",
            options=list(country_options.keys()),
            index=list(country_options.values()).index(st.session_state.selected_country) if st.session_state.selected_country in country_options.values() else 0,
            help="Manually select a different country if auto-detection is wrong"
        )

        st.session_state.selected_country = country_options[selected_display]

        st.write(f"**Active Country:** {CountryDetector.get_country_name(st.session_state.selected_country).upper()}")
        st.write(f"**LLM Model:** {settings.llm_model}")
        st.write(f"**Cache:** {'✅ Enabled' if settings.enable_cache else '❌ Disabled'}")

        st.divider()

    # Create custom tab navigation with session state control
    tab_names = ["📄 Upload Resume", "🔍 Search Jobs", "🏆 View Matches", "ℹ️ About"]
    tab_keys = ["upload", "search", "matches", "about"]

    # Map active tab to index
    if st.session_state.active_tab not in tab_keys:
        st.session_state.active_tab = "upload"

    current_index = tab_keys.index(st.session_state.active_tab)

    # Create tab selection
    selected_tab = st.radio(
        "Navigation",
        tab_names,
        index=current_index,
        horizontal=True,
        label_visibility="collapsed"
    )

    # Update active tab when user clicks
    new_index = tab_names.index(selected_tab)
    if tab_keys[new_index] != st.session_state.active_tab:
        st.session_state.active_tab = tab_keys[new_index]
        st.rerun()

    st.divider()

    # Render appropriate tab content
    if st.session_state.active_tab == "upload":
        upload_and_parse_tab()
    elif st.session_state.active_tab == "search":
        search_jobs_tab()
    elif st.session_state.active_tab == "matches":
        view_matches_tab()
    elif st.session_state.active_tab == "about":
        about_tab()


def upload_and_parse_tab():
    """Tab 1: Upload and parse resume"""

    st.header("📄 Step 1: Upload Your Resume")

    # Check if resume is already loaded
    if st.session_state.resume:
        resume = st.session_state.resume

        st.success("✅ Resume already loaded!")

        # Show quick summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Name", resume.name or "Not specified")
        with col2:
            st.metric("Target Roles", len(resume.target_job_titles) if resume.target_job_titles else 0)
        with col3:
            st.metric("Technical Skills", len(resume.technical_skills))

        st.info("""
        **Your resume is ready to use!**

        You can:
        - ✏️ Review and edit the information below
        - 🔍 Go to **Tab 2** to search for jobs
        - 📄 Or upload a different resume
        """)

        # Option to upload new resume
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📄 Upload Different Resume", type="secondary", use_container_width=True):
                st.session_state.resume = None
                st.session_state.jobs = None
                st.session_state.matched_jobs = None
                st.rerun()

        with col2:
            if st.button("🔍 Continue to Job Search →", type="primary", use_container_width=True):
                # Switch to Tab 2
                st.session_state.active_tab = "search"
                st.rerun()

        st.divider()

    else:
        # No resume loaded - show uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )

        if uploaded_file:
            # Save temporarily
            temp_path = Path("data/resumes") / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            st.success(f"✅ File uploaded: {uploaded_file.name}")

            # Parse button
            if st.button("🔍 Parse Resume", type="primary"):
                with st.spinner("🤖 AI is analyzing your resume..."):
                    try:
                        parser = ResumeParser()
                        resume = parser.parse(str(temp_path))
                        st.session_state.resume = resume
                        st.success("✅ Resume parsed successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error parsing resume: {str(e)}")
        else:
            # No file uploaded yet
            st.info("👆 Upload your resume PDF to get started!")
            return

    # Display parsed resume if available (for both cases)
    if st.session_state.resume:
        st.divider()
        st.subheader("✏️ Review & Edit Extracted Information")

        resume = st.session_state.resume

        # Personal Information
        with st.expander("👤 Personal Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", value=resume.name or "")
                email = st.text_input("Email", value=resume.email or "")
            with col2:
                location = st.text_input("Current Location", value=resume.current_location or "")
                years_exp = st.number_input("Years of Experience", value=resume.years_of_experience or 0, min_value=0, max_value=50)

        # Career Profile
        with st.expander("🎯 Career Profile", expanded=True):
            target_roles = st.text_area(
                "Target Job Titles (one per line)",
                value="\n".join(resume.target_job_titles) if resume.target_job_titles else "",
                help="Enter the job titles you're looking for"
            )

            col1, col2 = st.columns(2)
            with col1:
                career_level = st.selectbox(
                    "Career Level",
                    options=["Intern", "Junior", "Mid-Level", "Senior", "Lead", "Principal", "Executive"],
                    index=["Intern", "Junior", "Mid-Level", "Senior", "Lead", "Principal", "Executive"].index(resume.career_level) if resume.career_level else 2
                )
            with col2:
                remote_pref = st.selectbox(
                    "Remote Preference",
                    options=["On-site", "Hybrid", "Remote", "Flexible"],
                    index=["On-site", "Hybrid", "Remote", "Flexible"].index(resume.remote_preference) if resume.remote_preference else 3
                )

        # Skills
        with st.expander("💻 Skills", expanded=True):
            tech_skills = st.text_area(
                "Technical Skills (comma-separated)",
                value=", ".join(resume.technical_skills) if resume.technical_skills else "",
                help="e.g., Python, SQL, Machine Learning"
            )

            soft_skills = st.text_area(
                "Soft Skills (comma-separated)",
                value=", ".join(resume.soft_skills) if resume.soft_skills else "",
                help="e.g., Leadership, Communication, Problem Solving"
            )

            languages = st.text_area(
                "Languages (comma-separated)",
                value=", ".join(resume.languages) if resume.languages else "",
                help="e.g., English, French, Spanish"
            )

        # Work Experience
        with st.expander("💼 Work Experience", expanded=False):
            if resume.work_experience:
                for i, exp in enumerate(resume.work_experience, 1):
                    st.markdown(f"**Position {i}:**")
                    st.write(f"- **Title:** {exp.job_title}")
                    st.write(f"- **Company:** {exp.company_name}")
                    st.write(f"- **Duration:** {exp.duration}")
                    st.write(f"- **Industry:** {exp.industry}")
                    st.divider()
            else:
                st.info("No work experience extracted")

        # Education
        with st.expander("🎓 Education", expanded=False):
            if resume.education:
                for edu in resume.education:
                    st.write(f"- **{edu.level}** in {edu.field_of_study or 'N/A'}")
                    if edu.institution:
                        st.write(f"  {edu.institution}")
            else:
                st.info("No education information extracted")

        # Save changes button
        if st.button("💾 Save Changes", type="primary"):
            # Update resume with edited values
            resume.name = name
            resume.email = email
            resume.current_location = location
            resume.years_of_experience = years_exp
            resume.target_job_titles = [role.strip() for role in target_roles.split("\n") if role.strip()]
            resume.career_level = career_level
            resume.remote_preference = remote_pref
            resume.technical_skills = [skill.strip() for skill in tech_skills.split(",") if skill.strip()]
            resume.soft_skills = [skill.strip() for skill in soft_skills.split(",") if skill.strip()]
            resume.languages = [lang.strip() for lang in languages.split(",") if lang.strip()]

            st.session_state.resume = resume
            st.success("✅ Changes saved! You can now search for jobs.")

        # Quick summary
        st.divider()
        st.info(f"""
        **Summary:**
        - {len(resume.target_job_titles)} target roles
        - {len(resume.technical_skills)} technical skills
        - {len(resume.work_experience)} work experiences
        - {resume.years_of_experience} years of experience
        """)


def search_jobs_tab():
    """Tab 2: Search for jobs"""

    st.header("🔍 Step 2: Search for Jobs")

    if not st.session_state.resume:
        st.warning("⚠️ Please upload and parse your resume first (Tab 1)")
        return

    resume = st.session_state.resume

    # Search parameters
    col1, col2 = st.columns(2)

    with col1:
        # Default to first target role
        default_query = resume.target_job_titles[0] if resume.target_job_titles else ""
        job_query = st.text_input(
            "Job Title / Keywords",
            value=default_query,
            help="What job are you looking for?"
        )

    with col2:
        location = st.text_input(
            "Location",
            value=resume.current_location or "",
            help="Enter a specific city name (e.g., Antwerp, Brussels) OR leave empty to search the entire country. Country names won't work - use the sidebar to select your country.",
            placeholder="Leave empty for entire country"
        )

        # Validate location input
        location_error = None
        location_warning = None

        if location:
            # Check if user entered a country name instead of city
            country_in_location = CountryDetector.is_country_name_in_location(location)
            if country_in_location and country_in_location != st.session_state.selected_country:
                country_name = CountryDetector.get_country_name(country_in_location)
                location_error = f"⚠️ **Error:** You entered a country name (**{country_name}**). Please enter a **city name** instead, or **leave empty** to search the entire country, or change the country in the sidebar."
            elif country_in_location and country_in_location == st.session_state.selected_country:
                country_name = CountryDetector.get_country_name(country_in_location)
                location_warning = f"💡 **Tip:** Searching for '{country_name}' will return very few results. Instead, enter a specific city (e.g., Antwerp, Brussels) or **leave the field empty** to search all of {country_name}."
            else:
                # Check if city matches selected country
                if not CountryDetector.is_city_in_country(location, st.session_state.selected_country):
                    selected_country_name = CountryDetector.get_country_name(st.session_state.selected_country)
                    location_warning = f"⚠️ **Warning:** The city '**{location}**' doesn't appear to be in **{selected_country_name}**. If this is correct, change the country in the sidebar. Otherwise, check for typos."

            # Auto-detect country when location changes
            detected = CountryDetector.detect_country(location, default=settings.adzuna_country)
            if detected != st.session_state.detected_country:
                st.session_state.detected_country = detected
                # Only auto-update if no error
                if not location_error:
                    st.session_state.selected_country = detected
                    st.rerun()
        else:
            # Empty location - show helpful tip
            selected_country_name = CountryDetector.get_country_name(st.session_state.selected_country)
            st.info(f"💡 **Searching entire country:** All jobs in **{selected_country_name}** will be included.")

        # Display error or warning
        if location_error:
            st.error(location_error)
        elif location_warning:
            st.warning(location_warning)

    col3, col4 = st.columns(2)

    with col3:
        num_jobs = st.slider(
            "Number of Jobs to Fetch",
            min_value=10,
            max_value=50,
            value=20,
            step=5,
            help="How many job listings to retrieve from Adzuna. More jobs means: (1) Better chance of finding good matches, (2) Slightly slower processing. Adzuna allows max 50 jobs per search."
        )

    with col4:
        top_n_llm = st.slider(
            "Top N for LLM Scoring",
            min_value=5,
            max_value=20,
            value=10,
            step=5,
            help="After initial ranking by similarity, the top N jobs are analyzed in-depth by AI (GPT-4o-mini) to provide detailed match scores and explanations. Higher numbers = more detailed analysis but slower. Recommended: 10 for balance of speed and quality."
        )

    # Search button
    if st.button("🚀 Search & Match Jobs", type="primary"):
        # Check if user can use the app
        can_use, reason = can_use_app()

        if not can_use:
            st.error(f"""
            ❌ {reason}

            **Options:**
            1. Enter your OpenAI API key in the sidebar (get one free at platform.openai.com)
            2. Wait until tomorrow for your free demo query to refresh
            """)
            return

        # Validation before search
        if not job_query:
            st.error("❌ Please enter a job title or keywords")
            return

        # Note: Empty location is now allowed - searches entire country

        # Check for country name error only if location is provided
        if location:
            country_in_location = CountryDetector.is_country_name_in_location(location)
            if country_in_location and country_in_location != st.session_state.selected_country:
                country_name = CountryDetector.get_country_name(country_in_location)
                selected_name = CountryDetector.get_country_name(st.session_state.selected_country)
                st.error(f"""
                ❌ **Cannot search:** You entered '**{location}**' which is a country name.

                **Options:**
                1. Enter a city name in **{selected_name}** (e.g., Antwerp, Brussels)
                2. Leave location **empty** to search all of {selected_name}
                3. Change the country to **{country_name}** in the sidebar
                """)
                return

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Use demo query if not using own key
            if not has_user_api_key():
                if not use_demo_query(get_client_ip()):
                    st.error("Failed to use demo query. Please try again or enter your API key.")
                    return

            # Step 1: Fetch jobs
            status_text.text("🔍 Fetching jobs from Adzuna...")
            progress_bar.progress(25)

            # Use selected country for fetching
            fetcher = JobFetcher()
            # Temporarily override the country setting
            original_country = settings.adzuna_country
            settings.adzuna_country = st.session_state.selected_country
            fetcher.country = st.session_state.selected_country

            jobs = fetcher.search_jobs(
                query=job_query,
                location=location,
                results_per_page=num_jobs
            )

            # Restore original setting
            settings.adzuna_country = original_country

            if not jobs:
                st.error("❌ No jobs found. Try different search parameters.")
                return

            st.session_state.jobs = jobs
            progress_bar.progress(50)

            # Step 2: Match jobs
            status_text.text(f"🎯 Matching {len(jobs)} jobs with your resume...")
            progress_bar.progress(60)

            matcher = JobMatcher()
            matched_jobs = matcher.match_jobs(
                resume=resume,
                jobs=jobs,
                top_n_for_llm=top_n_llm
            )

            st.session_state.matched_jobs = matched_jobs
            progress_bar.progress(100)

            status_text.text("✅ Complete!")
            time.sleep(0.5)

            # Show success message
            st.success(f"""
            ✅ **Matching Complete!**

            Found {len(matched_jobs)} jobs. Top match: **{matched_jobs[0].job_title}** ({matched_jobs[0].match_score}%)

            Go to the **View Matches** tab to see results!
            """)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def view_matches_tab():
    """Tab 3: View matched jobs"""

    st.header("🏆 Step 3: Your Job Matches")

    if not st.session_state.matched_jobs:
        st.warning("⚠️ No matches yet. Please search for jobs first (Tab 2)")
        return

    matched_jobs = st.session_state.matched_jobs

    # Summary statistics
    jobs_with_scores = [j for j in matched_jobs if j.match_score is not None]
    avg_score = sum(j.match_score for j in jobs_with_scores) / len(jobs_with_scores) if jobs_with_scores else 0
    high_matches = [j for j in matched_jobs if j.match_score and j.match_score >= 70]
    medium_matches = [j for j in matched_jobs if j.match_score and 50 <= j.match_score < 70]
    low_matches = [j for j in matched_jobs if j.match_score and j.match_score < 50]

    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs", len(matched_jobs))
    col2.metric(
        "Avg Score",
        f"{avg_score:.1f}%",
        help="Average match score of all jobs that received AI scoring (typically the top 10 matches based on initial similarity)"
    )
    col3.metric("🟢 High (70+)", len(high_matches))
    col4.metric("🟡 Medium (50-69)", len(medium_matches))

    st.divider()

    # Filters
    st.subheader("🔧 Filter Results")
    col1, col2, col3 = st.columns(3)

    with col1:
        min_score = st.slider("Minimum Match Score", 0, 100, 50, 5)

    with col2:
        sort_by = st.selectbox("Sort By", ["Match Score", "Posted Date", "Salary"])

    with col3:
        show_explanation = st.checkbox("Show Explanations", value=True)

    # Filter jobs
    filtered_jobs = [j for j in matched_jobs if j.match_score and j.match_score >= min_score]

    if not filtered_jobs:
        st.warning(f"No jobs with score >= {min_score}%. Try lowering the threshold.")
        return

    st.info(f"Showing {len(filtered_jobs)} jobs (filtered from {len(matched_jobs)})")

    st.divider()

    # Display job cards
    st.subheader("📋 Matched Jobs")

    for i, job in enumerate(filtered_jobs, 1):
        # Determine score color
        if job.match_score >= 70:
            score_class = "match-score-high"
            badge = "🟢"
        elif job.match_score >= 50:
            score_class = "match-score-medium"
            badge = "🟡"
        else:
            score_class = "match-score-low"
            badge = "🔴"

        # Job card
        with st.container():
            # Card header with title
            col1, col2 = st.columns([3, 1])

            with col1:
                # Job title with rank badge
                st.markdown(f"""
                <div class="job-title">
                    <span class="rank-badge">#{i}</span>
                    {job.job_title}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**🏢 Company:** {job.company_name}")
                st.markdown(f"**📍 Location:** {job.location}")

                if job.contract_type:
                    st.markdown(f"**📋 Contract:** {job.contract_type}")

                if job.category:
                    st.markdown(f"**🏷️ Category:** {job.category}")

                if job.salary_min or job.salary_max:
                    salary_str = ""
                    if job.salary_min and job.salary_max:
                        salary_str = f"{job.salary_currency} {job.salary_min:,.0f} - {job.salary_max:,.0f}"
                    elif job.salary_min:
                        salary_str = f"{job.salary_currency} {job.salary_min:,.0f}+"
                    st.markdown(f"**💰 Salary:** {salary_str}")

                if job.posted_date:
                    st.markdown(f"**📅 Posted:** {job.posted_date}")

            with col2:
                st.markdown(f'<div class="{score_class}">{badge} {job.match_score}%</div>', unsafe_allow_html=True)
                st.markdown("**Match Score**")

            # Match explanation
            if show_explanation and job.match_explanation:
                with st.expander("💡 Why this matches"):
                    st.write(job.match_explanation)

            # Job description with "See more" functionality
            with st.expander("📄 Job Description"):
                description_preview_length = 500

                if len(job.description) > description_preview_length:
                    # Show preview first
                    if f"show_full_desc_{i}" not in st.session_state:
                        st.session_state[f"show_full_desc_{i}"] = False

                    if st.session_state[f"show_full_desc_{i}"]:
                        # Show full description
                        st.write(job.description)
                        if st.button("Show less", key=f"less_{i}"):
                            st.session_state[f"show_full_desc_{i}"] = False
                            st.rerun()
                    else:
                        # Show preview with "See more"
                        st.write(job.description[:description_preview_length] + "...")
                        if st.button("📖 See more", key=f"more_{i}", type="secondary"):
                            st.session_state[f"show_full_desc_{i}"] = True
                            st.rerun()
                else:
                    # Short description, show it all
                    st.write(job.description)

            # Apply button
            st.link_button("🔗 Apply Now", job.job_url, use_container_width=True)

            st.divider()

    # Export results
    st.subheader("💾 Export Results")
    if st.button("Download Results as JSON"):
        import json

        results = {
            "generated_at": datetime.now().isoformat(),
            "total_matches": len(matched_jobs),
            "filtered_matches": len(filtered_jobs),
            "summary": {
                "average_score": avg_score,
                "high_matches": len(high_matches),
                "medium_matches": len(medium_matches),
                "low_matches": len(low_matches)
            },
            "jobs": [
                {
                    "rank": i + 1,
                    "match_score": job.match_score,
                    "job_title": job.job_title,
                    "company": job.company_name,
                    "location": job.location,
                    "url": job.job_url,
                    "explanation": job.match_explanation,
                    "posted_date": str(job.posted_date) if job.posted_date else None
                }
                for i, job in enumerate(filtered_jobs)
            ]
        }

        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(results, indent=2),
            file_name=f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
