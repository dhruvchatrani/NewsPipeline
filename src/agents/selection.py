import os
import json
from typing import List
import google.generativeai as genai
import yaml
from ..core.models import RawTrend

class TrendSelector:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.history_path = "data/history.json"

    def _load_history(self) -> List[str]:
        if os.path.exists(self.history_path):
            with open(self.history_path, "r") as f:
                return json.load(f)
        return []

    def select_top_trends(self, trends: List[RawTrend], history: List[str] = None) -> List[RawTrend]:
        """Use Gemini to deduplicate, rank with scoring matrix, and filter history."""
        if not trends:
            return []

        history = history or self._load_history()
        history_str = "\n".join([f"- {h}" for h in history[-20:]])
        trend_list_str = "\n".join([f"- {t.title} (Source: {t.source})" for t in trends])

        weights = self.config["scoring_matrix"]
        count = self.config["pipeline"]["top_n_trends"]

        prompt = f"""
        Analyze the following news trends and select the top {count} unique stories.

        History (Avoid these recently covered stories):
        {history_str}

        Current Trends:
        {trend_list_str}

        Scoring Matrix (Weighting):
        - Geopolitical Impact: {weights['geopolitical_impact']}
        - Economic Consequences: {weights['economic_consequences']}
        - Human Interest: {weights['human_interest']}

        Tasks:
        1. Filter out stories that are substantially similar to the History.
        2. Deduplicate similar stories within the Current Trends.
        3. Rate each unique story on a scale of 0-10 for each criteria in the Scoring Matrix.
        4. Calculate a Weighted Score.
        5. Return the top {count} stories.

        Format your response strictly as a JSON list of objects:
        [
            {{
                "title": "Story Title",
                "weighted_score": 0.0,
                "justification": "Why this story was chosen based on the matrix"
            }}
        ]
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            selected_data = json.loads(response.text)

            final_trends = []
            for item in selected_data:
                match = next((t for t in trends if t.title.lower() in item["title"].lower() or item["title"].lower() in t.title.lower()), None)

                if match:
                    match.relevance_score = item["weighted_score"]
                    final_trends.append(match)
                else:
                    final_trends.append(RawTrend(
                        title=item["title"],
                        source="Aggregated",
                        relevance_score=item["weighted_score"]
                    ))

            return final_trends[:count]
        except Exception as e:
            print(f"Error in Trend Selection: {e}")
            return trends[:count]
