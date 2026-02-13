# Technical Details: Autonomous News Agent

This document provides a deep dive into the architecture, logic, and design decisions behind the NewsPipeline.

##  System Architecture

The system is designed as a modular pipeline to ensure robustness and clarity in data flow.

### 1. Ingestion Layer
*   **Strategy**: Hybrid approach using official APIs (NewsAPI, Google Trends) for broad coverage and targeted scrapers for deep content.
*   **Resilience**: Implements exponential backoff and rotation between multiple data sources to mitigate API failures.

### 2. Selection Layer (Trend Ranking Logic)
*   **Algorithm**: The `trend_score` (010) is calculated based on:
    *   **Velocity**: How fast the topic is gaining traction across sources.
    *   **Authority**: Weighted score based on the reputation of the source.
    *   **Clustering**: Frequency of the same event being reported under different headlines (Deduplication).
*   **Deduplication**: Uses semantic embeddings (e.g., `text-embedding-3-small`) to cluster similar stories (e.g., "BTC Price" and "Bitcoin Surge") into a single trend.

### 3. Research & Data Grounding
*   **RAG (Retrieval-Augmented Generation)**: The system fetches full-text articles and search results for the top##  LangGraph Orchestration & Self-Correction
The pipeline is orchestrated as a state machine using **LangGraph**. A key feature is the **Self-Correction Loop**:
1. **Verification**: After generation, a Critic agent breaks the article into individual claims and performs NLI-style verification against research snippets.
2. **Refinement**: If the article fails, the critique is sent back to the Generator for a targeted rewrite.
3. **Loop Control**: The state tracks `revision_count` to prevent infinite loops, defaulting to an exit after the `retry_limit` (configured in `config.yaml`).

##  Advanced Research Depth
*   **Multi-Source Search**: Powered by **Tavily**, the research agent triggers secondary searches to gather context from 5+ independent publishers.
*   **Recursive Gap Filling**: An LLM-driven "Gap Detector" identifies missing figures, dates, or names in the initial context and performs follow-up queries to fill those specific voids.

##  Selection Logic
*   **Scoring Matrix**: Trends are ranked based on a weighted matrix of Geopolitical Impact (40%), Economic Consequences (30%), and Human Interest (30%).
*   **History Persistence**: Avoids repetitive coverage by comparing current trends against `data/history.json` from previous executions.

##  Design Trade-offs

| Decision | Choice | Rationale |
| :--- | :--- | :--- |
| **Workflow** | Sequential Chains | Chosen for predictability and ease of debugging over autonomous agents for the core pipeline. |
| **Storage** | In-memory / JSON | Minimal overhead for a daily run; avoids the need for a persistent database like PostgreSQL. |
| **Logic** | Theory over Code | Prioritizes robust ranking algorithms and verification layers over complex crawling logic. |

##  Quality Control
*   **Factuality**: No "Pure LLM" generation is allowed. All drafts are strictly grounded in retrieved research snippets.
*   **Deduplication**: Employs cosine similarity thresholds to merge overlapping news streams.
*   **Error Handling**: If a search API fails, the system falls back to cached trends or secondary scrapers to ensure continuity.

##  Potential Extensions (Bonus)
*   **Verification Agent**: An asynchronous critique loop that provides a "Pass/Fail" on factual accuracy.
*   **Multi-Region Support**: Parameterized ingestion to filter trends by `US`, `India`, or `Global`.
*   **Dashboard**: A Streamlit interface for side-by-side comparison of trends and generated articles.
