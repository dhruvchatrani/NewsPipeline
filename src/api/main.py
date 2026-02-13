import os
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
import json
from dotenv import load_dotenv

from ..core.graph import graph
from ..core.models import PipelineOutput, Article

load_dotenv()

app = FastAPI(
    title="News Agent REST API",
    description="Strict JSON API for the Autonomous News Agent",
    version="2.0.0"
)

class ArticleOutput(BaseModel):
    title: str
    category: str
    trend_score: float
    summary: str
    article_body: str
    sources: List[str]
    hallucination_check: str

class NewsPipelineResponse(BaseModel):
    date: str
    execution_time_seconds: float
    articles: List[ArticleOutput]

@app.get("/", tags=["Health"])
def root():
    return {"status": "online", "message": "News Agent REST API is running."}

@app.post("/run", response_model=NewsPipelineResponse, tags=["Pipeline"])
async def run_pipeline(region: str = Query("Global", description="Region for news ingestion (Global, US, India)")):
    """
    Execute the full news pipeline and return strict JSON output.
    """
    start_time = time.time()

    history_path = "data/history.json"
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except:
            history = []

    initial_state = {
        "region": region,
        "raw_trends": [],
        "selected_trends": [],
        "research_results": [],
        "articles": [],
        "current_step": "start",
        "errors": [],
        "revision_count": 0,
        "history": history,
        "critiques": [],
        "evaluation_score": 0.0
    }

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

    execution_time = time.time() - start_time

    if final_state.get("selected_trends"):
        new_trends = [t.title for t in final_state["selected_trends"]]
        updated_history = (history + new_trends)[-100:]
        try:
            os.makedirs("data", exist_ok=True)
            with open(history_path, "w") as f:
                json.dump(updated_history, f, indent=2)
        except:
            pass

    output_articles = []
    for art in final_state.get("articles", []):
        output_articles.append(ArticleOutput(
            title=art.title,
            category=art.category,
            trend_score=art.trend_score,
            summary=art.summary,
            article_body=art.article_body,
            sources=art.sources,
            hallucination_check=art.hallucination_check
        ))

    response_data = NewsPipelineResponse(
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        execution_time_seconds=round(execution_time, 2),
        articles=output_articles
    )

    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
