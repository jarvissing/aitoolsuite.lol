"""Keyword research tools for the Antigravity agent."""

import json
import httpx
from typing import Optional
from config.settings import NICHE_KEYWORDS

async def discover_keywords(seed_keyword: str, category: str = "general") -> str:
    """
    Uses Google Autocomplete API to discover keyword variations.
    Groups suggestions by patterns.
    """
    url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={seed_keyword}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = data[1]
            else:
                suggestions = []
                
        patterns = {
            "best": [],
            "free": [],
            "online": [],
            "tool": [],
            "generator": [],
            "calculator": [],
            "other": []
        }
        
        for sug in suggestions:
            sug_lower = sug.lower()
            if "best " in sug_lower:
                patterns["best"].append(sug)
            elif "free " in sug_lower:
                patterns["free"].append(sug)
            elif "online " in sug_lower:
                patterns["online"].append(sug)
            elif " tool" in sug_lower:
                patterns["tool"].append(sug)
            elif " generator" in sug_lower:
                patterns["generator"].append(sug)
            elif " calculator" in sug_lower:
                patterns["calculator"].append(sug)
            else:
                patterns["other"].append(sug)
                
        output = f"Keyword Suggestions for '{seed_keyword}':\n"
        for pattern, items in patterns.items():
            if items:
                output += f"\n--- {pattern.upper()} ---\n"
                output += "\n".join(f"- {item}" for item in items)
                output += "\n"
                
        return output
    except Exception as e:
        return f"Error discovering keywords: {str(e)}"

async def analyze_serp_competition(keyword: str) -> str:
    """
    Analyzes SERP competition for a given keyword (simplified mock version).
    """
    # In a real scenario, this would scrape SERPs or use DataForSEO.
    estimated_difficulty = len(keyword) % 100  # Fake difficulty for now
    
    template = f"""SERP Analysis Template for: {keyword}
    
Estimated Difficulty: {estimated_difficulty}/100

What to look for in actual SERPs:
- Domain Authority Signals: Are top 10 results dominated by DR 80+ sites?
- Content Quality: Is the content directly answering the user's intent?
- Schema Presence: Do competitors use FAQ, WebApplication, or SoftwareApplication schema?

Recommendation based on difficulty ({estimated_difficulty}):
"""
    if estimated_difficulty < 30:
        template += "Low competition. High priority target."
    elif estimated_difficulty < 60:
        template += "Medium competition. Target if highly relevant."
    else:
        template += "High competition. Consider long-tail variations."
        
    return template

async def score_keyword_opportunity(keyword: str, estimated_volume: int, estimated_kd: int, estimated_cpc: float) -> str:
    """
    Scores the keyword opportunity based on volume, KD, and CPC.
    """
    revenue_score = (estimated_volume * estimated_cpc * 0.4) + ((100 - estimated_kd) * 0.6)
    
    if revenue_score > 70:
        tag = "Quick Win"
    elif revenue_score >= 40:
        tag = "Core Revenue"
    elif revenue_score >= 20:
        tag = "Volume Play"
    else:
        tag = "Skip"
        
    return f"""Keyword Opportunity Analysis: {keyword}
- Estimated Volume: {estimated_volume}
- Estimated KD: {estimated_kd}
- Estimated CPC: ${estimated_cpc:.2f}
----------------------------
Revenue Score: {revenue_score:.2f}
Recommendation Tag: {tag}
"""

def get_seed_keywords() -> str:
    """
    Returns the list of seed keywords from config.
    """
    if not NICHE_KEYWORDS:
        return "No seed keywords configured."
    return "Seed Keywords:\n" + "\n".join(f"- {kw}" for kw in NICHE_KEYWORDS)
