"""Data models for OpenClaw skills."""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class SkillCategory(Enum):
    """All available skill categories."""

    AI_MACHINE_LEARNING = "AI & Machine Learning"
    AUTOMATION_PRODUCTIVITY = "Automation & Productivity"
    CLOUD_INFRASTRUCTURE = "Cloud & Infrastructure"
    COMMUNICATION = "Communication"
    DEVELOPMENT_CODING = "Development & Coding"
    EDUCATION_KNOWLEDGE = "Education & Knowledge"
    FILE_DATA_MANAGEMENT = "File & Data Management"
    FINANCE_TRADING = "Finance & Trading"
    GAMING_ENTERTAINMENT = "Gaming & Entertainment"
    GENERAL = "General"
    HEALTH_WELLNESS = "Health & Wellness"
    MARKETING_BUSINESS = "Marketing & Business"
    MEDIA_CONTENT = "Media & Content"
    SEARCH_RESEARCH = "Search & Research"
    SECURITY_PRIVACY = "Security & Privacy"
    SOCIAL_MEDIA = "Social Media"
    SYSTEM_OS = "System & OS"
    UTILITIES = "Utilities"
    WEB_INTERNET = "Web & Internet"
    WRITING_CONTENT_CREATION = "Writing & Content Creation"


@dataclass
class Skill:
    """Represents a single OpenClaw skill."""

    name: str
    slug: str
    owner: str
    display_name: str
    description: str
    version: str
    category: SkillCategory
    user_invocable: bool
    allowed_tools: List[str]
    file_count: int
    path: str
    files: List[str]
    content: str  # Full SKILL.md content
    metadata: Dict = field(default_factory=dict)

    @property
    def full_slug(self) -> str:
        """Get the full slug (owner/slug)."""
        return f"{self.owner}/{self.slug}"

    def to_dict(self) -> Dict:
        """Convert skill to dictionary."""
        return {
            "name": self.name,
            "slug": self.slug,
            "owner": self.owner,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "user_invocable": self.user_invocable,
            "allowed_tools": self.allowed_tools,
            "file_count": self.file_count,
            "full_slug": self.full_slug,
            "path": str(self.path),
            "files": self.files,
        }


class SkillRegistry:
    """Registry that holds all loaded skills."""

    def __init__(self):
        """Initialize the skill registry."""
        self._skills: List[Skill] = []
        self._index: Dict[str, Skill] = {}

    @property
    def skills(self) -> List[Skill]:
        """Get all skills."""
        return self._skills

    @property
    def total_skills(self) -> int:
        """Get total number of skills."""
        return len(self._skills)

    @property
    def unique_owners(self) -> Set[str]:
        """Get unique skill owners."""
        return {skill.owner for skill in self._skills}

    @property
    def category_count(self) -> Dict[str, int]:
        """Get skill counts by category."""
        counts: Dict[str, int] = {}
        for category in SkillCategory:
            count = sum(1 for skill in self._skills if skill.category == category)
            if count > 0:
                counts[category.value] = count
        return counts

    def add_skill(self, skill: Skill) -> None:
        """Add a skill to the registry."""
        self._skills.append(skill)
        self._index[skill.full_slug] = skill

    def get_skill(self, full_slug: str) -> Optional[Skill]:
        """Get a skill by its full slug (owner/slug)."""
        return self._index.get(full_slug)

    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a specific category."""
        return [skill for skill in self._skills if skill.category == category]

    def get_skills_by_owner(self, owner: str) -> List[Skill]:
        """Get all skills by a specific owner."""
        return [skill for skill in self._skills if skill.owner == owner]

    def load_from_json(self, json_path: str) -> None:
        """Load skills from a JSON catalog file."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        skills_data = data if isinstance(data, list) else data.get("skills", data)
        if isinstance(skills_data, dict) and "skills" not in skills_data:
            skills_data = [skills_data]

        for item in skills_data:
            try:
                cat_str = item.get("category", "General")
                try:
                    category = SkillCategory(cat_str)
                except ValueError:
                    category = SkillCategory.GENERAL

                allowed_tools = item.get("allowed_tools", "")
                if isinstance(allowed_tools, str):
                    allowed_tools = [t.strip() for t in allowed_tools.split(",") if t.strip()] if allowed_tools else []

                skill = Skill(
                    name=item.get("name", item.get("slug", "")),
                    slug=item.get("slug", ""),
                    owner=item.get("owner", ""),
                    display_name=item.get("display_name", item.get("displayName", "")),
                    description=item.get("description", ""),
                    version=item.get("version", ""),
                    category=category,
                    user_invocable=item.get("user_invocable", True),
                    allowed_tools=allowed_tools,
                    file_count=item.get("file_count", 0),
                    path=item.get("path", ""),
                    files=item.get("files", []),
                    content=item.get("content", ""),
                    metadata=item.get("metadata", {}),
                )
                self.add_skill(skill)
            except Exception as e:
                continue


# Singleton instance
_skill_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    global _skill_registry
    if _skill_registry is None:
        _skill_registry = SkillRegistry()
        # Try to load from embedded catalog
        import importlib.resources as pkg_resources
        try:
            catalog_path = Path(__file__).parent.parent / "data" / "skill_catalog.json"
            if catalog_path.exists():
                _skill_registry.load_from_json(str(catalog_path))
        except Exception:
            pass
    return _skill_registry


def reset_skill_registry() -> None:
    """Reset the global skill registry (for testing)."""
    global _skill_registry
    _skill_registry = None
