import os
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
import yaml
from .models import AgentState, RawTrend, ResearchResult, Article
from ..services.ingestion import NewsIngestion
from ..agents.selection import TrendSelector
from ..services.research import NewsResearcher
from ..agents.generation import NewsGenerator
from ..agents.verification import VerificationAgent
from ..agents.evaluator import NewsEvaluator

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def ingest_node(state: AgentState) -> Dict[str, Any]:
    print(f"---INGESTING NEWS FOR {state['region']}---")
    ingestor = NewsIngestion()

    region_map = {
        "US": {"query": "trending US news", "rss": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"},
        "India": {"query": "trending India news", "rss": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"},
        "Global": {"query": "global news trends", "rss": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"}
    }

    cfg = region_map.get(state["region"], region_map["Global"])

    try:
        raw_trends = ingestor.get_all_trends(query=cfg["query"], rss_url=cfg["rss"])
        if not raw_trends:
            return {"errors": ["No trends found."], "current_step": "ingest_fail"}
        return {"raw_trends": raw_trends, "current_step": "ingest", "revision_count": 0}
    except Exception as e:
        return {"errors": [f"Ingestion failed: {e}"], "current_step": "ingest_error"}

def select_node(state: AgentState) -> Dict[str, Any]:
    print("---SELECTING TRENDS---")
    selector = TrendSelector()
    selected_trends = selector.select_top_trends(state["raw_trends"])
    return {"selected_trends": selected_trends, "current_step": "select"}

def research_node(state: AgentState) -> Dict[str, Any]:
    print("---RESEARCHING TRENDS---")
    researcher = NewsResearcher()
    research_results = researcher.research_all(state["selected_trends"])
    return {"research_results": research_results, "current_step": "research"}

def generate_node(state: AgentState) -> Dict[str, Any]:
    print("---GENERATING ARTICLES---")
    generator = NewsGenerator()
    articles = generator.generate_all(state["research_results"])
    return {"articles": articles, "current_step": "generate"}

def verify_node(state: AgentState) -> Dict[str, Any]:
    print("---VERIFYING ARTICLES---")
    verifier = VerificationAgent()
    verified_articles = []
    has_fail = False
    critiques = []

    for art, res in zip(state["articles"], state["research_results"]):
        verified_art = verifier.verify_article(art, res)
        verified_articles.append(verified_art)
        if verified_art.hallucination_check == "Fail":
            has_fail = True
            critiques.append(getattr(verified_art, 'critique', "General quality failure."))

    return {
        "articles": verified_articles,
        "current_step": "verify",
        "critiques": critiques,
        "revision_count": state.get("revision_count", 0) + (1 if has_fail else 0)
    }

def refine_node(state: AgentState) -> Dict[str, Any]:
    print(f"---REFINING ARTICLES (Revision #{state['revision_count']})---")
    generator = NewsGenerator()
    refined_articles = []

    for i, (art, res) in enumerate(zip(state["articles"], state["research_results"])):
        if art.hallucination_check == "Fail":
            critique = state["critiques"][i] if i < len(state["critiques"]) else "Please improve factuality."
            refined_art = generator.generate_article(res, critique=critique)
            refined_articles.append(refined_art)
        else:
            refined_articles.append(art)

    return {"articles": refined_articles, "current_step": "refine"}

def evaluate_node(state: AgentState) -> Dict[str, Any]:
    print("---FINAL EVALUATION (LLM-as-a-Judge)---")
    evaluator = NewsEvaluator()
    score = evaluator.evaluate_articles(state["articles"])
    return {"current_step": "evaluate", "evaluation_score": score}

def route_after_research(state: AgentState) -> str:
    if not state.get("research_results") or any(len(r.content_snippets) == 0 for r in state["research_results"]):
        print(" Research insufficient. Routing back to Selection.")
        return "select"
    return "generate"

def route_after_verify(state: AgentState) -> str:
    retry_limit = config["pipeline"]["retry_limit"]

    needs_refine = any(a.hallucination_check in ["Fail", "Unsure"] for a in state["articles"])

    if needs_refine and state["revision_count"] < retry_limit:
        print(f" Routing to Refine/Retry (Attempt {state['revision_count'] + 1}/{retry_limit}) due to: " +
              ", ".join([a.hallucination_check for a in state["articles"] if a.hallucination_check != "Pass"]))
        return "refine"

    if needs_refine:
        print(" Max revisions reached or some articles remained 'Unsure/Fail'. Proceeding to final evaluation.")
    else:
        print(" All articles passed verification.")
    return "evaluate"

def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("ingest", ingest_node)
    workflow.add_node("select", select_node)
    workflow.add_node("research", research_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("evaluate", evaluate_node)

    workflow.set_entry_point("ingest")

    workflow.add_edge("ingest", "select")
    workflow.add_edge("select", "research")

    workflow.add_conditional_edges(
        "research",
        route_after_research,
        {
            "select": "select",
            "generate": "generate"
        }
    )

    workflow.add_edge("generate", "verify")

    workflow.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "refine": "refine",
            "evaluate": "evaluate"
        }
    )

    workflow.add_edge("refine", "verify")
    workflow.add_edge("evaluate", END)

    return workflow.compile()

graph = create_graph()
