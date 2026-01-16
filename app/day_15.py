import streamlit as st
import time
import json
from snowflake.snowpark.functions import ai_complete

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()

if "latest_results" not in st.session_state:
    st.session_state.latest_results = None

def run_model(model: str, prompt: str) -> dict:
    """Execute model and collect metrics."""
    start = time.time()

    df = session.range(1).select(
        ai_complete(model=model, prompt=prompt).alias("response")
    )

    rows = df.collect()
    response_raw = rows[0][0]
    response_json = json.loads(response_raw)

    text = response_json.get("choices", [{}])[0].get("messages", "") if isinstance(response_json, dict) else str(response_json)

    latency = time.time() - start
    tokens = int(len(text.split()) * 4/3)  
    return {
        "latency": latency,
        "tokens": tokens,
        "response_text": text
    }

def display_metrics(results: dict, model_key: str):
    """Display metrics for a model."""
    latency_col, tokens_col = st.columns(2)  

    latency_col.metric("Latency (s)", f"{results[model_key]['latency']:.1f}")  
    tokens_col.metric("Tokens", results[model_key]['tokens'])

def display_response(container, results: dict, model_key: str):
    """Display chat messages in container."""
    with container:
        with st.chat_message("user"):
            st.write(results["prompt"])
        with st.chat_message("assistant"):
            st.write(results[model_key]["response_text"])

llm_models = [
    "llama3-8b",
    "llama3-70b",
    "mistral-7b",
    "mixtral-8x7b",
    "claude-3-5-sonnet",
    "claude-haiku-4-5",
    "openai-gpt-5",
    "openai-gpt-5-mini"
]
st.title(":material/compare: Select Models")
col_a, col_b = st.columns(2)  

col_a.write("**Model A**")
model_a = col_a.selectbox("Model A", llm_models, key="model_a", label_visibility="collapsed")

col_b.write("**Model B**")
model_b = col_b.selectbox("Model B", llm_models, key="model_b", index=1, label_visibility="collapsed")  # Default to second model

st.divider()
col_a, col_b = st.columns(2)  
results = st.session_state.latest_results

for col, model_name, model_key in [(col_a, model_a, "model_a"), (col_b, model_b, "model_b")]:
    with col:
        st.subheader(model_name)
        container = st.container(height=400, border=True)  

        if results:
            display_response(container, results, model_key)

        st.caption("Performance Metrics")
        if results:
            display_metrics(results, model_key)
        else:  
            latency_col, tokens_col = st.columns(2)
            latency_col.metric("Latency (s)", "—")
            tokens_col.metric("Tokens", "—")

st.divider()
if prompt := st.chat_input("Enter your message to compare models"):
    with st.status(f"Running {model_a}..."):
        result_a = run_model(model_a, prompt)
    with st.status(f"Running {model_b}..."):
        result_b = run_model(model_b, prompt)

    st.session_state.latest_results = {"prompt": prompt, "model_a": result_a, "model_b": result_b}
    st.rerun()  

st.divider()
st.caption("Day 15: Model Comparison Arena | 30 Days of AI")