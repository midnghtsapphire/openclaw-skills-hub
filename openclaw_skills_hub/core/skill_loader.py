"""Skill loading and parsing functionality."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.skill import Skill, SkillCategory

logger = logging.getLogger(__name__)

# Category keyword mapping for auto-categorization
CATEGORY_KEYWORDS = {
    "security": SkillCategory.SECURITY_PRIVACY,
    "password": SkillCategory.SECURITY_PRIVACY,
    "auth": SkillCategory.SECURITY_PRIVACY,
    "guard": SkillCategory.SECURITY_PRIVACY,
    "encrypt": SkillCategory.SECURITY_PRIVACY,
    "vpn": SkillCategory.SECURITY_PRIVACY,
    "search": SkillCategory.SEARCH_RESEARCH,
    "research": SkillCategory.SEARCH_RESEARCH,
    "browse": SkillCategory.SEARCH_RESEARCH,
    "scrape": SkillCategory.SEARCH_RESEARCH,
    "crawl": SkillCategory.SEARCH_RESEARCH,
    "google": SkillCategory.SEARCH_RESEARCH,
    "youtube": SkillCategory.MEDIA_CONTENT,
    "video": SkillCategory.MEDIA_CONTENT,
    "image": SkillCategory.MEDIA_CONTENT,
    "audio": SkillCategory.MEDIA_CONTENT,
    "music": SkillCategory.MEDIA_CONTENT,
    "podcast": SkillCategory.MEDIA_CONTENT,
    "photo": SkillCategory.MEDIA_CONTENT,
    "media": SkillCategory.MEDIA_CONTENT,
    "tiktok": SkillCategory.SOCIAL_MEDIA,
    "twitter": SkillCategory.SOCIAL_MEDIA,
    "instagram": SkillCategory.SOCIAL_MEDIA,
    "reddit": SkillCategory.SOCIAL_MEDIA,
    "social": SkillCategory.SOCIAL_MEDIA,
    "linkedin": SkillCategory.SOCIAL_MEDIA,
    "discord": SkillCategory.SOCIAL_MEDIA,
    "telegram": SkillCategory.SOCIAL_MEDIA,
    "slack": SkillCategory.COMMUNICATION,
    "email": SkillCategory.COMMUNICATION,
    "gmail": SkillCategory.COMMUNICATION,
    "chat": SkillCategory.COMMUNICATION,
    "message": SkillCategory.COMMUNICATION,
    "sms": SkillCategory.COMMUNICATION,
    "notification": SkillCategory.COMMUNICATION,
    "code": SkillCategory.DEVELOPMENT_CODING,
    "git": SkillCategory.DEVELOPMENT_CODING,
    "github": SkillCategory.DEVELOPMENT_CODING,
    "docker": SkillCategory.DEVELOPMENT_CODING,
    "deploy": SkillCategory.DEVELOPMENT_CODING,
    "debug": SkillCategory.DEVELOPMENT_CODING,
    "test": SkillCategory.DEVELOPMENT_CODING,
    "api": SkillCategory.DEVELOPMENT_CODING,
    "database": SkillCategory.DEVELOPMENT_CODING,
    "sql": SkillCategory.DEVELOPMENT_CODING,
    "developer": SkillCategory.DEVELOPMENT_CODING,
    "trading": SkillCategory.FINANCE_TRADING,
    "crypto": SkillCategory.FINANCE_TRADING,
    "wallet": SkillCategory.FINANCE_TRADING,
    "bitcoin": SkillCategory.FINANCE_TRADING,
    "defi": SkillCategory.FINANCE_TRADING,
    "stock": SkillCategory.FINANCE_TRADING,
    "finance": SkillCategory.FINANCE_TRADING,
    "payment": SkillCategory.FINANCE_TRADING,
    "invoice": SkillCategory.FINANCE_TRADING,
    "bank": SkillCategory.FINANCE_TRADING,
    "polymarket": SkillCategory.FINANCE_TRADING,
    "automation": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "workflow": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "schedule": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "task": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "productivity": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "calendar": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "notion": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "obsidian": SkillCategory.AUTOMATION_PRODUCTIVITY,
    "memory": SkillCategory.AI_MACHINE_LEARNING,
    "agent": SkillCategory.AI_MACHINE_LEARNING,
    "llm": SkillCategory.AI_MACHINE_LEARNING,
    "model": SkillCategory.AI_MACHINE_LEARNING,
    "generation": SkillCategory.AI_MACHINE_LEARNING,
    "prompt": SkillCategory.AI_MACHINE_LEARNING,
    "rag": SkillCategory.AI_MACHINE_LEARNING,
    "embedding": SkillCategory.AI_MACHINE_LEARNING,
    "book": SkillCategory.EDUCATION_KNOWLEDGE,
    "learn": SkillCategory.EDUCATION_KNOWLEDGE,
    "study": SkillCategory.EDUCATION_KNOWLEDGE,
    "tutor": SkillCategory.EDUCATION_KNOWLEDGE,
    "quiz": SkillCategory.EDUCATION_KNOWLEDGE,
    "math": SkillCategory.EDUCATION_KNOWLEDGE,
    "file": SkillCategory.FILE_DATA_MANAGEMENT,
    "data": SkillCategory.FILE_DATA_MANAGEMENT,
    "csv": SkillCategory.FILE_DATA_MANAGEMENT,
    "pdf": SkillCategory.FILE_DATA_MANAGEMENT,
    "document": SkillCategory.FILE_DATA_MANAGEMENT,
    "spreadsheet": SkillCategory.FILE_DATA_MANAGEMENT,
    "storage": SkillCategory.FILE_DATA_MANAGEMENT,
    "cloud": SkillCategory.CLOUD_INFRASTRUCTURE,
    "aws": SkillCategory.CLOUD_INFRASTRUCTURE,
    "server": SkillCategory.CLOUD_INFRASTRUCTURE,
    "kubernetes": SkillCategory.CLOUD_INFRASTRUCTURE,
    "linux": SkillCategory.CLOUD_INFRASTRUCTURE,
    "macos": SkillCategory.SYSTEM_OS,
    "windows": SkillCategory.SYSTEM_OS,
    "system": SkillCategory.SYSTEM_OS,
    "monitor": SkillCategory.SYSTEM_OS,
    "health": SkillCategory.HEALTH_WELLNESS,
    "fitness": SkillCategory.HEALTH_WELLNESS,
    "medical": SkillCategory.HEALTH_WELLNESS,
    "weather": SkillCategory.UTILITIES,
    "translate": SkillCategory.UTILITIES,
    "calculator": SkillCategory.UTILITIES,
    "convert": SkillCategory.UTILITIES,
    "time": SkillCategory.UTILITIES,
    "map": SkillCategory.UTILITIES,
    "game": SkillCategory.GAMING_ENTERTAINMENT,
    "play": SkillCategory.GAMING_ENTERTAINMENT,
    "trivia": SkillCategory.GAMING_ENTERTAINMENT,
    "web": SkillCategory.WEB_INTERNET,
    "website": SkillCategory.WEB_INTERNET,
    "html": SkillCategory.WEB_INTERNET,
    "css": SkillCategory.WEB_INTERNET,
    "seo": SkillCategory.WEB_INTERNET,
    "marketing": SkillCategory.MARKETING_BUSINESS,
    "sales": SkillCategory.MARKETING_BUSINESS,
    "crm": SkillCategory.MARKETING_BUSINESS,
    "analytics": SkillCategory.MARKETING_BUSINESS,
    "ads": SkillCategory.MARKETING_BUSINESS,
    "write": SkillCategory.WRITING_CONTENT_CREATION,
    "blog": SkillCategory.WRITING_CONTENT_CREATION,
    "content": SkillCategory.WRITING_CONTENT_CREATION,
    "article": SkillCategory.WRITING_CONTENT_CREATION,
    "nano": SkillCategory.AI_MACHINE_LEARNING,
}


class SkillLoader:
    """Loads and parses OpenClaw skills from disk."""

    def __init__(self, skills_dir: str):
        """Initialize the skill loader.

        Args:
            skills_dir: Directory containing skill directories
        """
        self.skills_dir = Path(skills_dir)
        if not self.skills_dir.exists():
            raise ValueError(f"Skills directory does not exist: {skills_dir}")

    def load_all_skills(self) -> List[Skill]:
        """Load all skills from the skills directory.

        Returns:
            List of loaded skills
        """
        skills = []
        seen_keys = set()

        for meta_path in self.skills_dir.rglob("_meta.json"):
            skill_dir = meta_path.parent
            try:
                skill = self._load_skill_from_dir(skill_dir)
                if skill and skill.full_slug not in seen_keys:
                    seen_keys.add(skill.full_slug)
                    skills.append(skill)
            except Exception as e:
                logger.debug(f"Failed to load skill from {skill_dir}: {e}")

        logger.info(f"Loaded {len(skills)} skills from {self.skills_dir}")
        return skills

    def _load_skill_from_dir(self, skill_dir: Path) -> Optional[Skill]:
        """Load a single skill from its directory."""
        meta_json = skill_dir / "_meta.json"
        skill_md = skill_dir / "SKILL.md"

        if not meta_json.exists():
            return None

        # Parse _meta.json
        try:
            with open(meta_json, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            return None

        owner = metadata.get("owner", "")
        slug = metadata.get("slug", "")
        display_name = metadata.get("displayName", slug)
        version = metadata.get("latest", {}).get("version", "")

        if not slug:
            return None

        # Parse SKILL.md frontmatter
        description = ""
        name_field = ""
        user_invocable = True
        allowed_tools_str = ""
        skill_content = ""

        if skill_md.exists():
            try:
                skill_content = skill_md.read_text(encoding="utf-8", errors="replace")
                frontmatter = self._parse_frontmatter(skill_content)
                description = frontmatter.get("description", "")
                name_field = frontmatter.get("name", "")
                uv = frontmatter.get("user-invocable", "true")
                user_invocable = str(uv).lower() != "false"
                allowed_tools_str = frontmatter.get("allowed-tools", "")
            except Exception:
                pass

        # Parse allowed tools
        allowed_tools = []
        if isinstance(allowed_tools_str, str) and allowed_tools_str:
            allowed_tools = [t.strip() for t in allowed_tools_str.split(",") if t.strip()]
        elif isinstance(allowed_tools_str, list):
            allowed_tools = allowed_tools_str

        # Count files
        all_files = []
        try:
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    all_files.append(str(f.relative_to(skill_dir)))
        except Exception:
            pass

        # Auto-categorize
        category = self._categorize_skill(display_name, description)

        return Skill(
            name=name_field or slug,
            slug=slug,
            owner=owner,
            display_name=display_name,
            description=description[:500] if description else "",
            version=version,
            category=category,
            user_invocable=user_invocable,
            allowed_tools=allowed_tools,
            file_count=len(all_files),
            path=str(skill_dir.relative_to(self.skills_dir)) if str(skill_dir).startswith(str(self.skills_dir)) else str(skill_dir),
            files=all_files[:20],
            content=skill_content[:2000] if skill_content else "",
            metadata=metadata,
        )

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse simple YAML-like frontmatter from SKILL.md content.

        Uses simple line-by-line parsing to avoid yaml dependency.
        """
        lines = content.split("\n")
        if not lines or lines[0].strip() != "---":
            return {}

        frontmatter = {}
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                break
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                frontmatter[key] = value

        return frontmatter

    def _categorize_skill(self, display_name: str, description: str) -> SkillCategory:
        """Auto-categorize a skill based on its name and description."""
        text = f"{display_name} {description}".lower()
        for keyword, category in CATEGORY_KEYWORDS.items():
            if keyword in text:
                return category
        return SkillCategory.GENERAL
