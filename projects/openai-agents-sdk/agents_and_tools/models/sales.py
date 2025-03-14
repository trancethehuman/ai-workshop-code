from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SalesContext:
    name: Optional[str]
    linkedin_url: Optional[str]
    profile_data: Optional[Dict[str, Any]]
    email_draft: Optional[str]
