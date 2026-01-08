import streamlit as st
import json
from snowflake.snowpark.functions import ai_complete

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()

@st.cache_data
def call_cortex_llm(prompt_text):
    """Makes a call to Cortex AI with the given prompt."""
    model = "claude-3-5-sonnet"
    df = session.range(1).select(
        ai_complete(model=model, prompt=prompt_text).alias("response")
    )

    response_raw = df.collect()[0][0]
    response_json = json.loads(response_raw)
    return response_json

st.title(":material/post: LinkedIn Post Generator v2")

content = st.text_input("Content URL:", "https://docs.snowflake.com/en/user-guide/views-semantic/overview")
tone = st.selectbox("Tone:", ["Professional", "Casual", "Funny"])
word_count = st.slider("Approximate word count:", 50, 300, 100)

if st.button("Generate Post"):
    with st.status("Starting engine...", expanded=True) as status:
        st.write(":material/psychology: Thinking: Analyzing constraints and tone...")
        prompt = f"""
        You are an expert social media manager. Generate a LinkedIn post based on the following:

        Tone: {tone}
        Desired Length: Approximately {word_count} words
        Use content from this URL: {content}

        Generate only the LinkedIn post text. Use dash for bullet points.
        """
        
        st.write(":material/flash_on: Generating: contacting Snowflake Cortex...")
        
        response = call_cortex_llm(prompt)
        
        st.write(":material/check_circle: Post generation completed!")
        status.update(label="Post Generated Successfully!", state="complete", expanded=False)

    st.subheader("Generated Post:")
    st.markdown(response)