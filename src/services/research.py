import os
import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict
import google.generativeai as genai
import yaml
from ..core.models import RawTrend, ResearchResult

class NewsResearcher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

    def _tavily_search(self, query: str, max_results: int = 5) -> List[Dict]:
        if not self.tavily_api_key:
            print("Warning: TAVILY_API_KEY not found. Falling back to basic scraping.")
            return []

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_raw_content": True
        }

        timeout = self.config["search"].get("timeout_seconds", 60)
        import time
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                return response.json().get("results", [])
            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                print(f"       Tavily search attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"      Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"       All {max_retries} attempts failed for query: {query}")
        return []

    def research_trend(self, trend: RawTrend) -> ResearchResult:
        """Gather deep context using multi-source search and recursive gaps detection."""
        print(f"   Searching for: {trend.title}")

        search_results = self._tavily_search(f"{trend.title} detailed latest news",
                                            max_results=self.config["search"]["max_results_per_trend"])

        snippets = []
        urls = []

        if search_results:
            for res in search_results:
                snippets.append(res.get("content", ""))
                urls.append(res.get("url", ""))
        else:
            if trend.url:
                try:
                    resp = requests.get(trend.url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    text = " ".join([p.get_text() for p in soup.find_all('p')])
                    snippets.append(text[:2000])
                    urls.append(trend.url)
                except: pass

        context = "\n".join(snippets)
        gap_prompt = f"""
        Analyze the following research context about "{trend.title}":
        ---
        {context[:4000]}
        ---
        Identify any missing critical information (e.g., specific dates, names of key figures, exact statistics, or conflicting reports).

        Return a JSON list of 1-2 specific search queries to fill these gaps.
        If no gaps are found, return an empty list [].
        """

        try:
            gap_response = self.model.generate_content(
                gap_prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            gap_queries = json.loads(gap_response.text)

            for item in gap_queries:
                query_str = ""
                if isinstance(item, str):
                    query_str = item
                elif isinstance(item, dict):
                    query_str = item.get("search_query") or item.get("query") or str(item)

                if query_str:
                    print(f"      Filling gap with query: {query_str}")
                    follow_up = self._tavily_search(query_str, max_results=2)
                    for res in follow_up:
                        snippets.append(res.get("content", ""))
                        if res.get("url") not in urls:
                            urls.append(res.get("url", ""))
        except Exception as e:
            print(f"Gap detection/follow-up failed: {e}")

        return ResearchResult(
            trend_title=trend.title,
            content_snippets=snippets,
            source_urls=list(set(urls)),
            trend_score=trend.relevance_score
        )

    def research_all(self, trends: List[RawTrend]) -> List[ResearchResult]:
        results = []
        for trend in trends:
            results.append(self.research_trend(trend))
        return results
