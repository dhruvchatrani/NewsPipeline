import streamlit as st
import json
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="NewsAgent Dashboard", page_icon="", layout="wide")

st.title(" Autonomous News Agent")
st.markdown("A daily autonomous system that identifies trending global events and generates fact-grounded articles.")

st.sidebar.header("Pipeline Controls")
region = st.sidebar.selectbox("Select Region", ["Global", "US", "India"])
run_pipeline = st.sidebar.button(" Run Pipeline")

if run_pipeline:
    with st.spinner(f"Running pipeline for {region}... this may take a minute."):
        try:
            result = subprocess.run(["python3", "main.py", region], capture_output=True, text=True)
            if result.returncode == 0:
                st.success(f"Pipeline executed successfully for {region}!")
            else:
                st.error(f"Pipeline failed: {result.stderr}")
        except Exception as e:
            st.error(f"Error running pipeline: {e}")

output_path = "data/output.json"
if os.path.exists(output_path):
    with open(output_path, "r") as f:
        data = json.load(f)

    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Execution Date", data["date"])
    with col2:
        st.metric("Execution Time", f"{data['execution_time_seconds']}s")

    st.subheader(f"Latest Articles ({len(data['articles'])})")

    for article in data["articles"]:
        with st.expander(f"**{article['title']}** - ({article['category']})"):
            st.markdown(f"**Trend Score:** {article['trend_score']} | **Hallucination Check:** {article['hallucination_check']}")
            st.markdown("---")
            st.markdown(article["article_body"])
            st.markdown("---")
            st.markdown("**Sources:**")
            for source in article["sources"]:
                st.markdown(f"- [{source}]({source})")
else:
    st.info("No output data found. Run the pipeline to generate articles.")

if run_pipeline and 'result' in locals():
    with st.expander("Show Console Output"):
        st.code(result.stdout)
