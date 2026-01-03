"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Public Boost API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    postgres_user: str = "trusted_user"
    postgres_password: str = "trusted_password"
    postgres_db: str = "trusted_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Encryption
    encryption_key: str = "your-encryption-key-change-in-production-32-chars!!"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str | None = None

    @property
    def redis_url(self) -> str:
        """Construct Redis URL from components."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Frontend URL for password reset links
    frontend_url: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # File Upload
    upload_dir: str = "uploads"
    max_upload_size: int = 5 * 1024 * 1024  # 5 MB

    # Email (SMTP)
    smtp_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@publicboost.com"
    smtp_from_name: str = "Public Boost"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )


settings = Settings()

