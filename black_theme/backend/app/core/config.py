from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =====================================================
    # APPLICATION
    # =====================================================
    APP_NAME: str = "Opportunity OS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # =====================================================
    # DATABASE
    # =====================================================
    DATABASE_URL: str

    # =====================================================
    # SECURITY
    # =====================================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =====================================================
    # SEARCH
    # =====================================================
    TAVILY_API_KEY: str = ""

    # =====================================================
    # LIVE JOB SEARCH
    # =====================================================
    JSEARCH_API_KEY: str = ""
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""

    # =====================================================
    # AI
    # =====================================================
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # =====================================================
    # EMAIL
    # =====================================================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # =====================================================
    # REDIS
    # =====================================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # =====================================================
    # FILE UPLOADS
    # =====================================================
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760

    # =====================================================
    # CORS
    # =====================================================
    BACKEND_CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000"
    )

    # =====================================================
    # LOGGING
    # =====================================================
    LOG_LEVEL: str = "INFO"

    # =====================================================
    # SCHEDULER
    # =====================================================
    HACKATHON_REFRESH_HOURS: int = 6
    JOB_REFRESH_HOURS: int = 6

    # =====================================================
    # OPPORTUNITY SETTINGS
    # =====================================================
    DEFAULT_COUNTRY: str = "India"
    DEFAULT_LANGUAGE: str = "en"
    MAX_RESULTS_PER_SOURCE: int = 20

    # =====================================================
    # AI RECOMMENDATION SETTINGS
    # =====================================================
    MATCH_THRESHOLD: float = 0.65
    TOP_RECOMMENDATIONS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()