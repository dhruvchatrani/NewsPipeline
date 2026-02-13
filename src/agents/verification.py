import os
import json
from typing import List, Dict
import google.generativeai as genai
from ..core.models import Article, ResearchResult, ClaimVerification

class VerificationAgent:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def verify_article(self, article: Article, research: ResearchResult) -> Article:
        """Decompose article into claims and verify against source snippets."""
        print(f"    Verifying: {article.title}")

        snippets_text = "\n---\n".join(research.content_snippets)

        prompt = f"""
        You are a fact-checking editor. Verify the following article against the provided source snippets.

        ARTICLE:
        {article.article_body}

        SOURCE SNIPPETS:
        {snippets_text}

        TASKS:
        1. Break down the article into its core factual claims.
        2. For each claim, check if it is supported by the source snippets.
        3. Identify any hallucinations, exaggerations, or missing context.
        4. Return a "Pass" only if all major claims are verified. Otherwise, return "Fail".

        Format your response strictly as a JSON object:
        {{
            "hallucination_check": "Pass" | "Fail",
            "claims": [
                {{
                    "claim": "The specific claim text",
                    "is_verified": true | false,
                    "source_url": "URL if found",
                    "reasoning": "Brief explanation"
                }}
            ],
            "critique": "Actionable feedback for the writer to fix any failures."
        }}
        """

        try:
            import time
            for attempt in range(3):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
                    )
                    data = json.loads(response.text)

                    article.hallucination_check = data["hallucination_check"]
                    article.claims = [ClaimVerification(**c) for c in data.get("claims", [])]
                    article.critique = data.get("critique", "")
                    return article
                except Exception as e:
                    if "500" in str(e) and attempt < 2:
                        print(f"      Got 500 error, retrying ({attempt+1}/3)...")
                        time.sleep(2)
                        continue
                    raise e
        except Exception as e:
            print(f"    Verification failed for '{article.title}': {e}")
            article.hallucination_check = "Unsure"
            article.critique = f"Verification system error: {e}"
            return article
