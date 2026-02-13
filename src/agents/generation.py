import os
import google.generativeai as genai
from typing import List, Optional
from ..core.models import Article, ResearchResult
import json
import yaml

class NewsGenerator:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

    def generate_article(self, research: ResearchResult, critique: Optional[str] = None) -> Article:
        """Generate or refine an article based on research and optional critique."""
        print(f"   {' Generating' if not critique else ' Refining'}: {research.trend_title}")

        snippets_text = "\n---\n".join(research.content_snippets)
        sources_list = "\n".join(research.source_urls)
        word_count = self.config["pipeline"]["article_word_count"]

        prompt = f"""
        You are an elite investigative journalist. Write a {word_count} word news article about "{research.trend_title}".

        RESEARCH CONTEXT:
        {snippets_text[:8000]}

        AVAILABLE SOURCE URLS (ONLY use these):
        {sources_list}

        {f"REVISION FEEDBACK (Fix these issues): {critique}" if critique else ""}

        STRUCTURE:
        1. Catchy Headline
        2. Immediate Context (The "Why now")
        3. Detailed Key Developments (Fact-grounded)
        4. Broader Implications (Geopolitical/Economic/Social)

        REQUIREMENTS:
        - Use Markdown for structure.
        - STRICTLY avoid any information not present in the research context.
        - Word count: ~{word_count} words.
        - For the "sources" field, ONLY include URLs from the AVAILABLE SOURCE URLS list above.

        Format your response strictly as a JSON object:
        {{
            "title": "Final Headline",
            "category": "Technology" | "Finance" | "Politics" | "Other",
            "summary": "TL;DR summary (2 sentences)",
            "article_body": "Full Markdown article",
            "sources": ["Full URL from list", "Another URL from list"]
        }}
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)

            actual_urls = set(research.source_urls)
            generated_urls = data.get("sources", [])
            valid_urls = [url for url in generated_urls if url in actual_urls]

            if not valid_urls or any("example.com" in url or "URL" in url for url in generated_urls):
                valid_urls = research.source_urls[:3]

            data["sources"] = valid_urls
            data["trend_score"] = research.trend_score
            data["hallucination_check"] = "Unsure"

            return Article(**data)
        except Exception as e:
            print(f"Generation failed: {e}")
            return None

    def generate_all(self, research_list: List[ResearchResult]) -> List[Article]:
        articles = []
        for res in research_list:
            art = self.generate_article(res)
            if art:
                articles.append(art)
        return articles
