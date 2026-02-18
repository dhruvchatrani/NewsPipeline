# Technical Details: Autonomous News Agent

This document provides a deep dive into the architecture, logic, and design decisions behind the NewsPipeline.

##  System Architecture

The system is designed as a modular pipeline orchestrated by **LangGraph**, ensuring robustness and clarity in data flow through a state machine.

### 1. Ingestion Layer
*   **Strategy**: Hybrid approach using official APIs (NewsAPI, Google Trends via RSS) for broad coverage and targeted scrapers for deep content.
*   **Regional Support**: Parameterized ingestion supports filtering trends by `US`, `India`, or `Global`.
*   **Resilience**: Implements exponential backoff and rotation between multiple data sources to mitigate API failures.

### 2. Selection Layer
*   **Gemini-Driven Selection**: Uses `gemini-2.5-flash` to analyze raw trends, deduplicate overlapping stories, and filter against `data/history.json` to avoid repetitive coverage.
*   **Scoring Matrix**: Trends are ranked based on a weighted matrix configured in `config.yaml`:
    *   **Geopolitical Impact** (40%)
    *   **Economic Consequences** (30%)
    *   **Human Interest** (30%)
*   **Deduplication**: Employs TF-IDF and Cosine Similarity (via `sklearn`) to merge similar news streams before LLM refinement.

### 3. Advanced Research & Recursive Data Grounding
*   **Multi-Source Search**: Powered by **Tavily**, the research agent performs advanced deep searches to gather context from multiple independent publishers.
*   **Recursive Gap Filling**: An LLM-driven "Gap Detector" analyzes initial search results to identify missing figures, dates, or names, triggering secondary targeted searches to fill those specific voids.

### 4. Generation & Self-Correction
*   **Factuality-First Prompting**: All articles are strictly grounded in retrieved research snippets; no "Pure LLM" hallucination is permitted.
*   **Self-Correction Loop**: 
    1. **Verification**: A Critic agent evaluates the draft against research snippets for hallucination and quality.
    2. **Refinement**: If verification fails, the critique is sent back to the Generator for a targeted rewrite.
    3. **Loop Control**: The state tracks `revision_count` to ensure exit after a `retry_limit` (defaulting to 3).
*   **Quantified Quality**: Final articles undergo a "LLM-as-a-Judge" evaluation to produce a quality score.

##  LangGraph Orchestration

The pipeline is modeled as a directed acyclic graph (with loops for refinement) using the following nodes:

| Node | Responsibility |
| :--- | :--- |
| **Ingest** | Fetches raw trends based on region. |
| **Select** | Deduplicates and ranks trends using the scoring matrix. |
| **Research** | Performs deep search and recursive gap filling. |
| **Generate** | Drafts the initial article based on research. |
| **Verify** | Checks for hallucinations and factual grounding. |
| **Refine** | (Conditional) Rewrites articles that fail verification. |
| **Evaluate** | Final LLM-as-a-Judge scoring before completion. |

##  User Interface (Dashboard)

A **Streamlit** dashboard provides a premium management interface for the pipeline:
*   **Controls**: Trigger pipeline runs for specific regions (`Global`, `US`, `India`).
*   **Execution Metrics**: Real-time tracking of execution time and date.
*   **Article Review**: Expandable view of generated articles, category labeling, trend scores, and source links.
*   **Transparency**: Option to view live console output for debug and monitoring.

##  Current Tech Stack

*   **Orchestration**: LangGraph
*   **LLMs**: Google Gemini (gemini-2.5-flash)
*   **Search/Research**: Tavily API
*   **UI/Interface**: Streamlit
*   **Core Logic**: Python (Pandas, Scikit-learn, BeautifulSoup)
*   **Storage**: Local JSON persistence (`history.json`, `output.json`)

##  Design Trade-offs

| Decision | Choice | Rationale |
| :--- | :--- | :--- |
| **Orchestration** | LangGraph State Machine | Superior to sequential chains for handling refinement loops and complex logic. |
| **LLM Selection** | Gemini 2.5 Flash | Optimized for speed and reasoning performance in grounding tasks. |
| **Persistence** | File-based JSON | Minimal overhead for high-velocity daily cycles; eliminates DB maintenance. |
