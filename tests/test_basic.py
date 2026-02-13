"""Basic tests for OpenClaw Skills Hub."""
import sys
sys.path.insert(0, '/home/ubuntu/openclaw-skills-hub')

from openclaw_skills_hub.models.skill import SkillRegistry, SkillCategory, get_skill_registry, reset_skill_registry
from openclaw_skills_hub.search.engine import SearchEngine

def test_registry_loads():
    """Test that the registry loads skills from embedded catalog."""
    reset_skill_registry()
    registry = get_skill_registry()
    assert registry.total_skills > 9000, f"Expected >9000 skills, got {registry.total_skills}"
    print(f"✓ Registry loaded {registry.total_skills} skills")

def test_categories():
    """Test category counts."""
    registry = get_skill_registry()
    counts = registry.category_count
    assert len(counts) > 0, "No categories found"
    assert "Security & Privacy" in counts, "Security category missing"
    print(f"✓ Found {len(counts)} categories")

def test_search():
    """Test search functionality."""
    registry = get_skill_registry()
    engine = SearchEngine(registry.skills)
    results = engine.search("security", max_results=10)
    assert len(results) > 0, "No search results"
    print(f"✓ Search returned {len(results)} results")

def test_skill_structure():
    """Test skill data structure."""
    registry = get_skill_registry()
    skill = registry.skills[0]
    assert skill.name, "Skill missing name"
    assert skill.owner, "Skill missing owner"
    assert skill.category, "Skill missing category"
    assert skill.full_slug, "Skill missing full_slug"
    print(f"✓ Skill structure valid: {skill.full_slug}")

if __name__ == "__main__":
    print("Running OpenClaw Skills Hub tests...")
    test_registry_loads()
    test_categories()
    test_search()
    test_skill_structure()
    print("\n✅ All tests passed!")
