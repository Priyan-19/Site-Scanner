"""
SiteScanner Core - Configuration
Config-driven architecture using pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="SiteScanner Core", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175",
        env="ALLOWED_ORIGINS"
    )

    # Rate limiting
    rate_limit: str = Field(default="10/minute", env="RATE_LIMIT")

    # Scan config
    scan_timeout: int = Field(default=60, env="SCAN_TIMEOUT")
    port_scan_timeout: float = Field(default=1.0, env="PORT_SCAN_TIMEOUT")
    max_scan_history: int = Field(default=100, env="MAX_SCAN_HISTORY")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Ports to scan
    target_ports: List[int] = [80, 443, 21, 22, 25, 53, 8080, 8443, 3306, 5432]

    # Subdomains to check (passive only)
    passive_subdomains: List[str] = [
        "api", "dev", "admin", "test", "staging",
        "mail", "beta", "app", "www", "cdn",
        "dashboard", "portal", "static", "media"
    ]

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
