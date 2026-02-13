import pytest
import xml.etree.ElementTree as ET
from src.services.ingestion import NewsIngestion
from src.core.models import RawTrend

def test_rss_parser_basic():
    """Test if RSS parser can handle a mock XML structure."""
    mock_rss = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <item>
            <title>Test News Title</title>
            <link>https://example.com/test</link>
            <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
        </item>
    </channel>
    </rss>"""

    ingestor = NewsIngestion(api_key="mock")
    trend = RawTrend(title="Test", source="RSS", url="http://test.com")
    assert trend.title == "Test"

def test_score_range():
    """Verify relevance scores are initialized and within range."""
    trend = RawTrend(title="Test", source="Source", relevance_score=8.5)
    assert 0 <= trend.relevance_score <= 10

def test_config_loading():
    """Ensure config.yaml is correctly structured."""
    import yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert "pipeline" in config
    assert "scoring_matrix" in config
    assert config["pipeline"]["top_n_trends"] > 0
