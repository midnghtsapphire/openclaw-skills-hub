"""Configuration management for OpenClaw Skills Hub."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    
    # Skills directory path (can be overridden via env)
    skills_dir: Path = Path("/home/ubuntu/openclaw-skills-repo/skills")
    
    # API server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Search settings
    search_fuzzy_threshold: float = 0.6
    search_max_results: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Catalog settings
    catalog_cache_ttl: int = 3600  # seconds
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            skills_dir=Path(os.getenv("SKILLS_DIR", cls.skills_dir)),
            api_host=os.getenv("API_HOST", cls.api_host),
            api_port=int(os.getenv("API_PORT", cls.api_port)),
            api_reload=os.getenv("API_RELOAD", str(cls.api_reload)).lower() == "true",
            search_fuzzy_threshold=float(os.getenv("SEARCH_FUZZY_THRESHOLD", cls.search_fuzzy_threshold)),
            search_max_results=int(os.getenv("SEARCH_MAX_RESULTS", cls.search_max_results)),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            log_format=os.getenv("LOG_FORMAT", cls.log_format),
            catalog_cache_ttl=int(os.getenv("CATALOG_CACHE_TTL", cls.catalog_cache_ttl)),
        )


# Global configuration instance
config = Config.from_env()
