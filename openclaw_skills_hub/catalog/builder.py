"""Catalog builder for OpenClaw skills."""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

from ..models.skill import Skill, SkillCategory, SkillRegistry
from ..core.skill_loader import SkillLoader


logger = logging.getLogger(__name__)


class CatalogBuilder:
    """Builds and exports the skills catalog."""
    
    def __init__(self, skills_dir: Path):
        """Initialize the catalog builder.
        
        Args:
            skills_dir: Directory containing skills
        """
        self.skills_dir = skills_dir
        self.loader = SkillLoader(skills_dir)
        self.registry = SkillRegistry()
    
    def build_catalog(self) -> SkillRegistry:
        """Build the complete skills catalog.
        
        Returns:
            Populated skill registry
        """
        logger.info("Building skills catalog...")
        
        skills = self.loader.load_all_skills()
        for skill in skills:
            self.registry.add_skill(skill)
        
        logger.info(f"Catalog built with {len(skills)} skills")
        return self.registry
    
    def generate_statistics(self) -> Dict:
        """Generate catalog statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "total_skills": self.registry.total_skills,
            "categories": {},
            "unique_owners": len(self.registry.unique_owners),
            "top_owners": {},
        }
        
        # Category counts
        for category in SkillCategory:
            count = len(self.registry.get_skills_by_category(category))
            stats["categories"][category.value] = count
        
        # Top owners
        owner_counts = {}
        for skill in self.registry.skills:
            owner_counts[skill.owner] = owner_counts.get(skill.owner, 0) + 1
        
        top_owners = sorted(owner_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats["top_owners"] = dict(top_owners)
        
        return stats
    
    def export_json(self, output_path: Path) -> None:
        """Export catalog to JSON.
        
        Args:
            output_path: Output file path
        """
        data = {
            "skills": [],
            "statistics": self.generate_statistics(),
        }
        
        for skill in self.registry.skills:
            skill_data = {
                "name": skill.name,
                "slug": skill.slug,
                "owner": skill.owner,
                "display_name": skill.display_name,
                "description": skill.description,
                "version": skill.version,
                "category": skill.category.value,
                "user_invocable": skill.user_invocable,
                "allowed_tools": skill.allowed_tools,
                "file_count": skill.file_count,
                "full_slug": skill.full_slug,
            }
            data["skills"].append(skill_data)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported catalog to JSON: {output_path}")
    
    def export_csv(self, output_path: Path) -> None:
        """Export catalog to CSV.
        
        Args:
            output_path: Output file path
        """
        fieldnames = [
            "name",
            "slug",
            "owner",
            "display_name",
            "description",
            "version",
            "category",
            "user_invocable",
            "allowed_tools",
            "file_count",
            "full_slug",
        ]
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for skill in self.registry.skills:
                row = {
                    "name": skill.name,
                    "slug": skill.slug,
                    "owner": skill.owner,
                    "display_name": skill.display_name,
                    "description": skill.description,
                    "version": skill.version,
                    "category": skill.category.value,
                    "user_invocable": skill.user_invocable,
                    "allowed_tools": ", ".join(skill.allowed_tools),
                    "file_count": skill.file_count,
                    "full_slug": skill.full_slug,
                }
                writer.writerow(row)
        
        logger.info(f"Exported catalog to CSV: {output_path}")
    
    def export_html(self, output_path: Path) -> None:
        """Export catalog to HTML.
        
        Args:
            output_path: Output file path
        """
        stats = self.generate_statistics()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Skills Hub</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .stats {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .skill {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
        .skill h3 {{ margin-top: 0; color: #333; }}
        .skill .meta {{ color: #666; font-size: 0.9em; }}
        .category {{ display: inline-block; background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }}
    </style>
</head>
<body>
    <h1>OpenClaw Skills Hub</h1>
    
    <div class="stats">
        <h2>Statistics</h2>
        <p><strong>Total Skills:</strong> {stats["total_skills"]}</p>
        <p><strong>Unique Owners:</strong> {stats["unique_owners"]}</p>
        
        <h3>Skills by Category</h3>
        <ul>
        """
        
        for category, count in stats["categories"].items():
            html_content += f"<li><strong>{category}:</strong> {count}</li>\n"
        
        html_content += """
        </ul>
    </div>
    
    <h2>All Skills</h2>
    """
        
        # Group skills by category
        skills_by_category = {}
        for skill in sorted(self.registry.skills, key=lambda s: (s.category.value, s.name)):
            if skill.category.value not in skills_by_category:
                skills_by_category[skill.category.value] = []
            skills_by_category[skill.category.value].append(skill)
        
        for category, skills in sorted(skills_by_category.items()):
            html_content += f"<h3>{category}</h3>\n"
            
            for skill in skills:
                html_content += f"""
    <div class="skill">
        <h3>{skill.display_name}</h3>
        <div class="meta">
            <span class="category">{skill.category.value}</span> |
            <strong>Owner:</strong> {skill.owner} |
            <strong>Version:</strong> {skill.version} |
            <strong>Files:</strong> {skill.file_count}
        </div>
        <p>{skill.description}</p>
    </div>
                """
        
        html_content += """
</body>
</html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Exported catalog to HTML: {output_path}")
