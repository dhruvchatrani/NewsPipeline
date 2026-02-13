import os
import json
from typing import List, Dict
import google.generativeai as genai
from ..core.models import Article

class NewsEvaluator:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def evaluate_articles(self, articles: List[Article]) -> float:
        """Evaluate articles for Journalistic Integrity and Factuality."""
        if not articles:
            return 0.0

        print(f"    Evaluating {len(articles)} articles...")

        combined_text = ""
        for i, art in enumerate(articles):
            combined_text += f"\nARTICLE {i+1}: {art.title}\n{art.article_body[:1000]}...\n"

        prompt = f"""
        You are a senior journalism professor. Evaluate the following articles on a scale of 1-10 across:
        1. Journalistic Integrity (Objectivity, Tone)
        2. Factuality (Groundedness in snippets)
        3. Clarity and Structure

        ARTICLES:
        {combined_text}

        Return a single JSON object with the average score:
        {{
            "average_score": 8.5,
            "justification": "Overall high quality..."
        }}
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return float(data.get("average_score", 0.0))
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return 5.0
