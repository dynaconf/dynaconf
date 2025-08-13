"""Example settings file with type annotations for testing generate command."""

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Annotated

# Type alias for documentation
Doc = lambda x: x

# Basic settings with type annotations
DEBUG: Annotated[bool, Doc("Enable debug mode for the application")] = False
PORT: Annotated[int, Doc("Port number for the web server")] = 8000
HOST: str = "localhost"
SECRET_KEY: Optional[str] = None

# Complex types
ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
DATABASE_CONFIG: Dict[str, str] = {
    "ENGINE": "sqlite3",
    "NAME": "db.sqlite3"
}

# Settings without documentation
CACHE_TIMEOUT: int = 300
LOG_LEVEL: str = "INFO"

# Optional settings
EMAIL_BACKEND: Optional[str] = None
REDIS_URL: Annotated[Optional[str], Doc("Redis connection URL for caching")] = None