import streamlit as st
from snowflake.snowpark.functions import ai_complete
import json

st.title(":material/smart_toy: Hello, Cortex!")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()


model = "claude-3-5-sonnet"
prompt = st.text_input("Enter your prompt: ")

if st.button("Generate Response"):
    df = session.range(1).select(
        ai_complete(model=model, prompt=prompt).alias("response")
    )

    response_raw = df.collect()[0][0]
    response = json.loads(response_raw)
    st.write(response)

st.divider()
st.caption("Day 2: Hello, Cortext! | 30 Days of AI")