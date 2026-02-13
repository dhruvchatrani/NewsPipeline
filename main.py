import os
import time
from datetime import datetime
from dotenv import load_dotenv
import json

from src.core.models import PipelineOutput
from src.core.graph import graph

def main():
    import sys
    region = sys.argv[1] if len(sys.argv) > 1 else "Global"

    start_time = time.time()
    load_dotenv()

    print(f" Starting Autonomous News Agent [Advanced Phase] [Region: {region}]...")

    history_path = "data/history.json"
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except: history = []

    initial_state = {
        "region": region,
        "raw_trends": [],
        "selected_trends": [],
        "research_results": [],
        "articles": [],
        "current_step": "start",
        "errors": [],
        "revision_count": 0,
        "history": history,
        "critiques": [],
        "evaluation_score": 0.0
    }

    try:
        final_state = graph.invoke(initial_state)
        print(" Graph execution complete.")
    except Exception as e:
        print(f" Graph execution failed: {e}")
        import traceback
        traceback.print_exc()
        return

    execution_time = time.time() - start_time

    eval_score = final_state.get("evaluation_score", 0.0)

    output = PipelineOutput(
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        execution_time_seconds=round(execution_time, 2),
        articles=final_state["articles"],
        evaluation_score=eval_score
    )

    output_path = "data/output.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output.model_dump(), f, indent=2)

    new_history = history + [t.title for t in final_state.get("selected_trends", [])]
    with open(history_path, "w") as f:
        json.dump(new_history[-100:], f, indent=2)

    print(f" Pipeline complete! Result saved to {output_path}")
    print(f" Evaluation Score: {eval_score}/10")
    print(f" Total execution time: {round(execution_time, 2)}s")

if __name__ == "__main__":
    main()
