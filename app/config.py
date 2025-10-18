"""
Configuration management using Pydantic Settings
"""
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # ===================================
    # LLM Configuration
    # ===================================
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    # ===================================
    # Job Platform Configuration
    # ===================================
    adzuna_app_id: Optional[str] = None
    adzuna_api_key: Optional[str] = None
    adzuna_country: str = "us"
    adzuna_results_per_page: int = 50
    adzuna_max_pages: int = 3
    adzuna_base_url: str = "https://api.adzuna.com/v1/api"

    # ===================================
    # Vector Store Configuration
    # ===================================
    vector_store_type: Literal["faiss", "chroma"] = "faiss"
    vector_store_path: Path = Path("./data/vector_store")

    # ===================================
    # Application Settings
    # ===================================
    env: Literal["development", "production"] = "development"
    log_level: str = "INFO"
    app_name: str = "AI Job Matcher"
    app_version: str = "0.1.0"

    # ===================================
    # Matching Engine Settings
    # ===================================
    min_match_score: int = 50
    top_n_matches: int = 10
    use_semantic_search: bool = True
    use_llm_scoring: bool = True
    similarity_threshold: float = 0.7

    # Weighting for composite score
    semantic_weight: float = 0.4
    keyword_weight: float = 0.3
    llm_score_weight: float = 0.3

    # ===================================
    # Caching Configuration
    # ===================================
    redis_host: str = "redis"
    redis_port: int = 6379
    cache_ttl: int = 3600  # 1 hour
    enable_cache: bool = True

    # ===================================
    # Rate Limiting
    # ===================================
    max_requests_per_hour: int = 100
    enable_rate_limit: bool = True

    # ===================================
    # Security & Privacy
    # ===================================
    secure_mode: bool = False
    delete_uploaded_files: bool = True
    data_retention_days: int = 7
    max_file_size_mb: int = 10

    # ===================================
    # Performance Tuning
    # ===================================
    batch_size: int = 10
    max_workers: int = 4
    embedding_cache_size: int = 1000

    # ===================================
    # Paths
    # ===================================
    data_dir: Path = Path("./data")
    resume_dir: Path = Path("./data/resumes")
    cache_dir: Path = Path("./data/cache")
    log_dir: Path = Path("./logs")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.resume_dir.mkdir(exist_ok=True)
        self.vector_store_path.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env == "production"

    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        return self.openai_api_key is not None and len(self.openai_api_key) > 0

    @property
    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured"""
        return self.anthropic_api_key is not None and len(self.anthropic_api_key) > 0

    @property
    def has_adzuna_credentials(self) -> bool:
        """Check if Adzuna credentials are configured"""
        return (
            self.adzuna_app_id is not None
            and self.adzuna_api_key is not None
            and len(self.adzuna_app_id) > 0
            and len(self.adzuna_api_key) > 0
        )

    def validate_api_keys(self) -> dict[str, bool]:
        """Validate all API keys and return status"""
        return {
            "openai": self.has_openai_key,
            "anthropic": self.has_anthropic_key,
            "adzuna": self.has_adzuna_credentials,
        }

    def get_adzuna_url(self, endpoint: str) -> str:
        """Construct Adzuna API URL"""
        return f"{self.adzuna_base_url}/jobs/{self.adzuna_country}/{endpoint}"


# Global settings instance
settings = Settings()


# Validation on import
if __name__ == "__main__":
    print("Configuration Status:")
    print("=" * 50)
    validation = settings.validate_api_keys()
    for service, status in validation.items():
        status_str = "✓ Configured" if status else "✗ Missing"
        print(f"{service.capitalize()}: {status_str}")
    print("=" * 50)
    print(f"Environment: {settings.env}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Vector Store: {settings.vector_store_type}")
    print(f"Cache Enabled: {settings.enable_cache}")
