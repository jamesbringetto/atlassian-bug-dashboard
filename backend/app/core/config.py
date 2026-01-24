"""
Core configuration for the Atlassian Bug Dashboard API.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://atlassian_user:atlassian_pass@localhost:5432/atlassian_bugs"
    
    # Jira
    JIRA_BASE_URL: str = "https://jira.atlassian.com"
    JIRA_PROJECT: str = "MIG"
    JIRA_ISSUE_TYPE: str = "Bug"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def origins_list(self) -> list[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
