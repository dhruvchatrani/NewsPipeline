import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from .models import RawTrend
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def deduplicate_trends(trends: List[RawTrend]) -> List[RawTrend]:
    """Deduplicate trends using TF-IDF + Cosine Similarity."""
    if not trends:
        return []

    method = config.get("deduplication", {}).get("method", "tfidf")
    threshold = config.get("deduplication", {}).get("threshold", 0.3)

    if method != "tfidf" or len(trends) < 2:
        return trends

    titles = [t.title for t in trends]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(titles)
    
    # Compute similarity matrix
    sim_matrix = cosine_similarity(tfidf_matrix)
    
    to_remove = set()
    unique_trends = []
    
    for i in range(len(trends)):
        if i in to_remove:
            continue
            
        unique_trends.append(trends[i])
        
        for j in range(i + 1, len(trends)):
            if sim_matrix[i, j] > threshold:
                to_remove.add(j)
                # print(f"Deduplicated: '{trends[j].title}' (Similar to '{trends[i].title}')")
                
    return unique_trends
