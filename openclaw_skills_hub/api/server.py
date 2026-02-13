"""FastAPI server for OpenClaw Skills Hub."""

import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..config import config
from ..models.skill import Skill, SkillCategory, SkillRegistry, get_skill_registry
from ..search.engine import SearchEngine


logger = logging.getLogger(__name__)


# Pydantic models for API responses
class SkillResponse(BaseModel):
    """Skill response model."""
    
    name: str
    slug: str
    owner: str
    display_name: str
    description: str
    version: str
    category: str
    user_invocable: bool
    allowed_tools: List[str]
    file_count: int
    full_slug: str


class SkillListResponse(BaseModel):
    """Skill list response model."""
    
    skills: List[SkillResponse]
    total: int
    page: int
    per_page: int


class CategoryResponse(BaseModel):
    """Category response model."""
    
    name: str
    count: int


class StatisticsResponse(BaseModel):
    """Statistics response model."""
    
    total_skills: int
    unique_owners: int
    categories: Dict[str, int]
    top_owners: Dict[str, int]


class SkillContentResponse(BaseModel):
    """Skill content response model."""
    
    content: str


def create_app() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title="OpenClaw Skills Hub API",
        description="Unified catalog of OpenClaw community skills",
        version="1.0.0",
    )
    
    # Get skill registry
    registry = get_skill_registry()
    search_engine = SearchEngine(registry.skills)
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize application."""
        logger.info("OpenClaw Skills Hub API starting up...")
    
    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "name": "OpenClaw Skills Hub API",
            "version": "1.0.0",
            "endpoints": {
                "skills": "/api/skills",
                "categories": "/api/categories",
                "stats": "/api/stats",
            },
        }
    
    @app.get("/api/skills", response_model=SkillListResponse)
    async def list_skills(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        category: Optional[str] = None,
        owner: Optional[str] = None,
    ):
        """List all skills with pagination."""
        skills = registry.skills
        
        # Apply filters
        if category:
            try:
                cat = SkillCategory(category)
                skills = [s for s in skills if s.category == cat]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        if owner:
            skills = [s for s in skills if s.owner == owner]
        
        # Pagination
        total = len(skills)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_skills = skills[start:end]
        
        # Convert to response models
        skill_responses = [
            SkillResponse(
                name=s.name,
                slug=s.slug,
                owner=s.owner,
                display_name=s.display_name,
                description=s.description,
                version=s.version,
                category=s.category.value,
                user_invocable=s.user_invocable,
                allowed_tools=s.allowed_tools,
                file_count=s.file_count,
                full_slug=s.full_slug,
            )
            for s in paginated_skills
        ]
        
        return SkillListResponse(
            skills=skill_responses,
            total=total,
            page=page,
            per_page=per_page,
        )
    
    @app.get("/api/skills/{owner}/{slug}", response_model=SkillResponse)
    async def get_skill(owner: str, slug: str):
        """Get skill details."""
        skill = None
        for s in registry.skills:
            if s.owner == owner and s.slug == slug:
                skill = s
                break
        
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return SkillResponse(
            name=skill.name,
            slug=skill.slug,
            owner=skill.owner,
            display_name=skill.display_name,
            description=skill.description,
            version=skill.version,
            category=skill.category.value,
            user_invocable=skill.user_invocable,
            allowed_tools=skill.allowed_tools,
            file_count=skill.file_count,
            full_slug=skill.full_slug,
        )
    
    @app.get("/api/skills/search", response_model=SkillListResponse)
    async def search_skills(
        q: str = Query(..., min_length=1),
        category: Optional[str] = None,
        owner: Optional[str] = None,
        max_results: int = Query(50, ge=1, le=200),
    ):
        """Search for skills."""
        # Parse category filter
        cat_filter = None
        if category:
            try:
                cat_filter = SkillCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Perform search
        results = search_engine.search(
            query=q,
            category=cat_filter,
            owner=owner,
            max_results=max_results,
        )
        
        # Convert to response models
        skill_responses = [
            SkillResponse(
                name=s.name,
                slug=s.slug,
                owner=s.owner,
                display_name=s.display_name,
                description=s.description,
                version=s.version,
                category=s.category.value,
                user_invocable=s.user_invocable,
                allowed_tools=s.allowed_tools,
                file_count=s.file_count,
                full_slug=s.full_slug,
            )
            for s in results
        ]
        
        return SkillListResponse(
            skills=skill_responses,
            total=len(results),
            page=1,
            per_page=len(results),
        )
    
    @app.get("/api/categories", response_model=List[CategoryResponse])
    async def list_categories():
        """List all categories with skill counts."""
        category_counts = registry.category_count
        
        return [
            CategoryResponse(name=category, count=count)
            for category, count in sorted(category_counts.items())
            if count > 0
        ]
    
    @app.get("/api/stats", response_model=StatisticsResponse)
    async def get_statistics():
        """Get catalog statistics."""
        from ..catalog.builder import CatalogBuilder
        
        builder = CatalogBuilder(config.skills_dir)
        builder.registry = registry
        stats = builder.generate_statistics()
        
        return StatisticsResponse(
            total_skills=stats["total_skills"],
            unique_owners=stats["unique_owners"],
            categories=stats["categories"],
            top_owners=stats.get("top_owners", {}),
        )
    
    @app.get("/api/skills/{owner}/{slug}/content", response_model=SkillContentResponse)
    async def get_skill_content(owner: str, slug: str):
        """Get skill content (SKILL.md)."""
        skill = None
        for s in registry.skills:
            if s.owner == owner and s.slug == slug:
                skill = s
                break
        
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return SkillContentResponse(content=skill.content)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "skills_loaded": len(registry.skills)}
    
    return app


def run_server():
    """Run the API server."""
    import uvicorn
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        reload=config.api_reload,
    )


if __name__ == "__main__":
    run_server()
