# AI-Powered Job Matcher

An intelligent job matching system that analyzes resumes and matches them with the best-fitting job opportunities using AI and semantic search.

## Features

- 📄 **Resume Analysis**: Extract and structure information from PDF resumes
- 🔍 **Smart Job Search**: Fetch jobs from Adzuna API based on resume profile
- 🤖 **AI-Powered Matching**: Semantic similarity + LLM-based scoring
- 📊 **Match Scoring**: Percentage-based compatibility scores with explanations
- 💬 **Query Refinement**: Natural language queries to filter and refine results
- 🚀 **Dockerized**: Easy deployment with Docker Compose

## Architecture

```
Resume (PDF) → Parser → Structured Data
                              ↓
                    Embedding Generation
                              ↓
Job API → Fetcher → Job Listings → Vector Store
                              ↓
                    Semantic Matching + LLM Scoring
                              ↓
                    Ranked Results (with %)
```

## Tech Stack

- **Framework**: LangChain, Streamlit
- **LLM**: OpenAI GPT / Anthropic Claude
- **Vector Store**: FAISS / ChromaDB
- **Job API**: Adzuna (free tier: 1000 calls/month)
- **Caching**: Redis
- **Infrastructure**: Docker, Docker Compose

## Prerequisites

- Docker & Docker Compose
- API Keys:
  - OpenAI or Anthropic (for LLM)
  - Adzuna (free at https://developer.adzuna.com/)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd job-matcher
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Build and Run

```bash
docker-compose up --build
```

### 4. Access Application

Open your browser and navigate to: `http://localhost:8501`

## Project Structure

```
ai-job-matcher/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── app/
│   ├── main.py               # Streamlit application
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic data models
│   ├── resume_parser.py      # PDF parsing & extraction
│   ├── job_fetcher.py        # Adzuna API integration
│   ├── matcher.py            # Matching engine
│   └── utils.py              # Helper functions
│
├── data/
│   ├── resumes/              # Uploaded resumes (temporary)
│   ├── vector_store/         # FAISS index storage
│   └── cache/                # API response cache
│
├── logs/                     # Application logs
│
└── tests/                    # Unit tests
    ├── test_parser.py
    ├── test_fetcher.py
    └── test_matcher.py
```

## Configuration

Key settings in `.env`:

```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Job Platform
ADZUNA_APP_ID=your-app-id
ADZUNA_API_KEY=your-api-key

# Models
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small

# Matching
MIN_MATCH_SCORE=60
TOP_N_MATCHES=10
USE_LLM_SCORING=true
```

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/main.py
```

### Testing

```bash
pytest tests/
```

## Usage

1. **Upload Resume**: Drop a PDF resume in the upload area
2. **View Analysis**: See extracted skills, experience, and preferences
3. **Get Matches**: Click "Find Matches" to search for jobs
4. **Review Results**: Browse ranked jobs with match percentages
5. **Refine Search**: Use natural language queries to filter results

## Roadmap

- [x] Phase 1: Basic resume parsing and job matching
- [ ] Phase 2: Query refinement with conversational interface
- [ ] Phase 3: Multi-platform job aggregation
- [ ] Phase 4: Application tracking and management
- [ ] Phase 5: Auto-generate cover letters

## API Rate Limits

- **Adzuna Free Tier**: 1,000 calls/month
- **OpenAI**: Pay-as-you-go (track usage in dashboard)
- **Anthropic**: Pay-as-you-go

## Troubleshooting

### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### API Key Errors
- Verify keys in `.env` are correct
- Check API quotas in provider dashboards

### Vector Store Issues
```bash
# Clear vector store
rm -rf data/vector_store/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check documentation at `/docs`

---

**Built with ❤️ using LangChain and Streamlit**
