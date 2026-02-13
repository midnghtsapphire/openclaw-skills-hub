"""Search engine for OpenClaw skills."""

import logging
import re
from typing import List, Optional, Set

from ..models.skill import Skill, SkillCategory


logger = logging.getLogger(__name__)


class SearchEngine:
    """Full-text search engine for skills."""
    
    def __init__(self, skills: List[Skill]):
        """Initialize the search engine.
        
        Args:
            skills: List of skills to search
        """
        self.skills = skills
        self._build_index()
    
    def _build_index(self):
        """Build search index."""
        logger.info(f"Building search index for {len(self.skills)} skills")
        
        # Create normalized search text for each skill
        self._skill_texts = []
        for skill in self.skills:
            text = " ".join([
                skill.name.lower(),
                skill.display_name.lower(),
                skill.description.lower(),
                skill.content.lower(),
                skill.owner.lower(),
                skill.category.value.lower(),
            ])
            self._skill_texts.append(text)
    
    def search(
        self,
        query: str,
        category: Optional[SkillCategory] = None,
        owner: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Skill]:
        """Search for skills.
        
        Args:
            query: Search query
            category: Filter by category
            owner: Filter by owner
            max_results: Maximum number of results
            
        Returns:
            List of matching skills
        """
        if not query and not category and not owner:
            return self.skills[:max_results]
        
        query_lower = query.lower() if query else ""
        results = []
        scores = []
        
        for i, skill in enumerate(self.skills):
            # Apply filters
            if category and skill.category != category:
                continue
            if owner and skill.owner != owner:
                continue
            
            # Calculate relevance score
            score = 0
            skill_text = self._skill_texts[i]
            
            if query_lower:
                # Exact matches get higher scores
                if query_lower in skill.name.lower():
                    score += 10
                if query_lower in skill.display_name.lower():
                    score += 8
                if query_lower in skill.description.lower():
                    score += 6
                if query_lower in skill.owner.lower():
                    score += 4
                if query_lower in skill.category.value.lower():
                    score += 3
                if query_lower in skill.content.lower():
                    score += 1
                
                # Word-based matching
                query_words = query_lower.split()
                skill_words = skill_text.split()
                word_matches = sum(1 for word in query_words if word in skill_words)
                score += word_matches * 2
            
            if score > 0:
                results.append(skill)
                scores.append(score)
        
        # Sort by score (descending) and return top results
        if scores:
            sorted_pairs = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
            results = [skill for _, skill in sorted_pairs]
        
        return results[:max_results]
    
    def fuzzy_search(
        self,
        query: str,
        threshold: float = 0.6,
        **kwargs
    ) -> List[Skill]:
        """Fuzzy search for skills.
        
        Args:
            query: Search query
            threshold: Similarity threshold (0.0-1.0)
            **kwargs: Additional search parameters
            
        Returns:
            List of matching skills
        """
        # Simple fuzzy matching based on character similarity
        query_lower = query.lower()
        results = []
        
        for skill in self.skills:
            # Calculate similarity for different fields
            similarities = []
            
            for text in [
                skill.name,
                skill.display_name,
                skill.description,
                skill.owner,
            ]:
                similarity = self._calculate_similarity(query_lower, text.lower())
                similarities.append(similarity)
            
            max_similarity = max(similarities) if similarities else 0
            
            if max_similarity >= threshold:
                results.append(skill)
        
        # Apply additional filters
        if kwargs.get("category"):
            results = [s for s in results if s.category == kwargs["category"]]
        if kwargs.get("owner"):
            results = [s for s in results if s.owner == kwargs["owner"]]
        
        max_results = kwargs.get("max_results", 50)
        return results[:max_results]
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity."""
        if not s1 or not s2:
            return 0.0
        
        # Count common characters
        common = sum(1 for c in s1 if c in s2)
        total = max(len(s1), len(s2))
        
        return common / total if total > 0 else 0.0
