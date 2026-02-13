from typing import List, Literal, Optional, TypedDict, Annotated, Dict
from pydantic import BaseModel, Field
import operator

class RawTrend(BaseModel):
    title: str
    source: str
    url: Optional[str] = None
    timestamp: Optional[str] = None
    relevance_score: float = 0.0

class ResearchResult(BaseModel):
    trend_title: str
    content_snippets: List[str]
    source_urls: List[str]
    trend_score: float = 0.0

class ClaimVerification(BaseModel):
    claim: str
    is_verified: bool
    source_url: Optional[str] = None
    reasoning: str

class Article(BaseModel):
    title: str
    category: Literal["Technology", "Finance", "Politics", "Other"]
    trend_score: float = Field(..., description="Normalized (0-10) or absolute score")
    summary: str = Field(..., description="TL;DR summary")
    article_body: str = Field(..., description="Comprehensive article body (600-800 words, Markdown supported)")
    sources: List[str]
    hallucination_check: Literal["Pass", "Fail", "Unsure"]
    claims: Optional[List[ClaimVerification]] = None
    critique: Optional[str] = None

class PipelineOutput(BaseModel):
    date: str = Field(..., description="Strict ISO 8601 (UTC)")
    execution_time_seconds: float
    articles: List[Article]
    evaluation_score: Optional[float] = None

class AgentState(TypedDict):
    region: str
    raw_trends: List[RawTrend]
    selected_trends: List[RawTrend]
    research_results: List[ResearchResult]
    articles: List[Article]
    current_step: str
    errors: List[str]
    revision_count: int
    history: List[str]
    critiques: List[str]
    evaluation_score: float
