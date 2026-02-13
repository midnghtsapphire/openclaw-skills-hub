"""Command-line interface for OpenClaw Skills Hub."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from ..config import config
from ..models.skill import SkillRegistry, get_skill_registry
from ..search.engine import SearchEngine
from ..catalog.builder import CatalogBuilder


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format,
)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format=config.log_format)


def list_skills(args):
    """List all skills with pagination."""
    registry = get_skill_registry()
    skills = registry.skills
    
    # Pagination
    page = args.page - 1
    per_page = args.per_page
    start = page * per_page
    end = start + per_page
    
    paginated_skills = skills[start:end]
    
    print(f"Skills {start + 1}-{min(end, len(skills))} of {len(skills)}:")
    print("-" * 80)
    
    for skill in paginated_skills:
        print(f"{skill.full_slug}")
        print(f"  Name: {skill.display_name}")
        print(f"  Category: {skill.category.value}")
        print(f"  Description: {skill.description[:100]}...")
        print()


def search_skills(args):
    """Search for skills."""
    registry = get_skill_registry()
    engine = SearchEngine(registry.skills)
    
    results = engine.search(
        query=args.query,
        category=args.category,
        owner=args.owner,
        max_results=args.max_results,
    )
    
    if not results:
        print("No skills found matching your search criteria.")
        return
    
    print(f"Found {len(results)} skills:")
    print("-" * 80)
    
    for skill in results:
        print(f"{skill.full_slug}")
        print(f"  Name: {skill.display_name}")
        print(f"  Category: {skill.category.value}")
        print(f"  Description: {skill.description[:100]}...")
        print()


def show_skill_info(args):
    """Show detailed skill information."""
    registry = get_skill_registry()
    
    # Parse owner/slug
    if "/" in args.skill:
        owner, slug = args.skill.split("/", 1)
    else:
        print("Error: Please specify skill as 'owner/slug'")
        return
    
    # Find skill
    skill = None
    for s in registry.skills:
        if s.owner == owner and s.slug == slug:
            skill = s
            break
    
    if not skill:
        print(f"Skill not found: {args.skill}")
        return
    
    print(f"Skill: {skill.display_name}")
    print("=" * 80)
    print(f"Slug: {skill.full_slug}")
    print(f"Version: {skill.version}")
    print(f"Category: {skill.category.value}")
    print(f"User Invocable: {skill.user_invocable}")
    print(f"Files: {skill.file_count}")
    print(f"Allowed Tools: {', '.join(skill.allowed_tools) or 'None'}")
    print()
    print("Description:")
    print(skill.description)
    print()
    
    if args.show_content:
        print("SKILL.md Content:")
        print("-" * 80)
        print(skill.content)


def list_categories(args):
    """List all categories with skill counts."""
    registry = get_skill_registry()
    category_counts = registry.category_count
    
    print("Skill Categories:")
    print("-" * 40)
    
    for category, count in sorted(category_counts.items()):
        if count > 0 or args.all:
            print(f"{category}: {count}")


def export_catalog(args):
    """Export catalog to various formats."""
    registry = get_skill_registry()
    builder = CatalogBuilder(config.skills_dir)
    builder.registry = registry
    
    output_path = Path(args.output)
    
    if args.format == "json":
        builder.export_json(output_path)
    elif args.format == "csv":
        builder.export_csv(output_path)
    elif args.format == "html":
        builder.export_html(output_path)
    else:
        print(f"Unsupported format: {args.format}")
        return
    
    print(f"Catalog exported to: {output_path}")


def run_skill(args):
    """Display skill instructions."""
    registry = get_skill_registry()
    
    # Parse owner/slug
    if "/" in args.skill:
        owner, slug = args.skill.split("/", 1)
    else:
        print("Error: Please specify skill as 'owner/slug'")
        return
    
    # Find skill
    skill = None
    for s in registry.skills:
        if s.owner == owner and s.slug == slug:
            skill = s
            break
    
    if not skill:
        print(f"Skill not found: {args.skill}")
        return
    
    print(f"Instructions for {skill.display_name}:")
    print("=" * 80)
    print(skill.content)


def show_stats(args):
    """Show catalog statistics."""
    registry = get_skill_registry()
    builder = CatalogBuilder(config.skills_dir)
    builder.registry = registry
    
    stats = builder.generate_statistics()
    
    print("OpenClaw Skills Hub Statistics")
    print("=" * 50)
    print(f"Total Skills: {stats['total_skills']:,}")
    print(f"Unique Owners: {stats['unique_owners']:,}")
    print()
    
    print("Skills by Category:")
    print("-" * 30)
    for category, count in sorted(stats["categories"].items()):
        if count > 0:
            print(f"  {category}: {count:,}")
    
    if stats.get("top_owners"):
        print("\nTop Contributors:")
        print("-" * 20)
        for owner, count in list(stats["top_owners"].items())[:10]:
            print(f"  {owner}: {count} skills")


def install_skill(args):
    """Install a skill to local directory."""
    registry = get_skill_registry()
    
    # Parse owner/slug
    if "/" in args.skill:
        owner, slug = args.skill.split("/", 1)
    else:
        print("Error: Please specify skill as 'owner/slug'")
        return
    
    # Find skill
    skill = None
    for s in registry.skills:
        if s.owner == owner and s.slug == slug:
            skill = s
            break
    
    if not skill:
        print(f"Skill not found: {args.skill}")
        return
    
    # Copy skill files
    import shutil
    
    output_dir = Path(args.output) if args.output else Path.cwd() / f"{owner}-{slug}"
    
    try:
        shutil.copytree(skill.path, output_dir)
        print(f"Skill installed to: {output_dir}")
    except Exception as e:
        print(f"Failed to install skill: {e}")


def build_catalog(args):
    """Build the skills catalog from scratch."""
    print("Building skills catalog...")
    
    try:
        builder = CatalogBuilder(config.skills_dir)
        registry = builder.build_catalog()
        
        print(f"Catalog built successfully with {len(registry.skills)} skills")
        
        if args.export:
            # Export in all formats
            base_path = Path(args.export)
            builder.export_json(base_path.with_suffix(".json"))
            builder.export_csv(base_path.with_suffix(".csv"))
            builder.export_html(base_path.with_suffix(".html"))
            print(f"Catalog exported to: {base_path}.{{json,csv,html}}")
    
    except Exception as e:
        print(f"Failed to build catalog: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenClaw Skills Hub - Unified catalog of OpenClaw community skills"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all skills")
    list_parser.add_argument("--page", type=int, default=1, help="Page number")
    list_parser.add_argument("--per-page", type=int, default=20, help="Skills per page")
    list_parser.set_defaults(func=list_skills)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search skills")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", help="Filter by category")
    search_parser.add_argument("--owner", help="Filter by owner")
    search_parser.add_argument("--max-results", type=int, default=50, help="Maximum results")
    search_parser.set_defaults(func=search_skills)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show skill details")
    info_parser.add_argument("skill", help="Skill identifier (owner/slug)")
    info_parser.add_argument("--show-content", action="store_true", help="Show full SKILL.md content")
    info_parser.set_defaults(func=show_skill_info)
    
    # Categories command
    cat_parser = subparsers.add_parser("categories", help="List categories")
    cat_parser.add_argument("--all", action="store_true", help="Show all categories including empty ones")
    cat_parser.set_defaults(func=list_categories)
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export catalog")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument("--format", choices=["json", "csv", "html"], default="json", help="Export format")
    export_parser.set_defaults(func=export_catalog)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Display skill instructions")
    run_parser.add_argument("skill", help="Skill identifier (owner/slug)")
    run_parser.set_defaults(func=run_skill)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=show_stats)
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install skill locally")
    install_parser.add_argument("skill", help="Skill identifier (owner/slug)")
    install_parser.add_argument("--output", help="Output directory")
    install_parser.set_defaults(func=install_skill)
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build catalog from scratch")
    build_parser.add_argument("--export", help="Export catalog after building")
    build_parser.set_defaults(func=build_catalog)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return 1
    except Exception as e:
        logger.exception("Command failed")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
