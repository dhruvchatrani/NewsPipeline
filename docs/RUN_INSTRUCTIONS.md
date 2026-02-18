# Run Instructions: NewsPipeline

Follow these steps to set up the environment and execute the Autonomous News Agent.

## 1. Environment Setup

### Prerequisites
- Python 3.10 or higher installed.
- Access to terminal/command line.

### Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd NewsPipeline
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Configuration

### API Keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
NEWS_API_KEY=your_news_api_key
```

- **GEMINI_API_KEY**: Required for LLM reasoning, deduplication, and generation.
- **TAVILY_API_KEY**: Required for deep research and recursive gap filling.
- **NEWS_API_KEY**: Required for initial trend ingestion.

## 3. Execution Modes

### Mode A: Traditional CLI (Recommended for Automation)
Run the pipeline directly from the terminal.
```bash
python3 main.py Global  # Options: Global, US, India
```

### Mode B: Streamlit Dashboard (Recommended for Review)
Launch the interactive web interface.
```bash
streamlit run src/ui/dashboard.py
```
- Select your region from the sidebar.
- Click **"Run Pipeline"**.
- View real-time console logs and formatted results.

### Mode C: REST API
Start the FastAPI server.
```bash
uvicorn src.api.main:app --reload
```
Trigger a run via `curl`:
```bash
curl -X POST "http://localhost:8000/run?region=Global"
```

## 4. Troubleshooting
- **ModuleNotFoundError**: Ensure you are inside the virtual environment (`source .venv/bin/activate`).
- **Authentication Error**: Double-check your API keys in the `.env` file.
- **Rate Limits**: If you encounter 429 errors from Tavily, the system will automatically retry with exponential backoff.
