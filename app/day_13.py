import streamlit as st
import json
from snowflake.snowpark.functions import ai_complete
import time

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()

def call_llm(prompt_text: str) -> str:
    """Call Snowflake Cortex LLM."""
    df = session.range(1).select(
        ai_complete(model="claude-3-5-sonnet", prompt=prompt_text).alias("response")
    )
    response_raw = df.collect()[0][0]
    response_json = json.loads(response_raw)
    if isinstance(response_json, dict):
        return response_json.get("choices", [{}])[0].get("messages", "")
    return str(response_json)

st.title(":material/chat: Customizable Chatbot")

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful pirate assistant named Captain Starlight. You speak with pirate slang, use nautical metaphors, and end sentences with 'Arrr!' when appropriate. Be helpful but stay in character."

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ahoy! Captain Starlight here, ready to help ye navigate the high seas of knowledge! Arrr!"}
    ]

with st.sidebar:
    st.header(":material/theater_comedy: Bot Personality")

    st.subheader("Quick Presets")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(":material/sailing: Pirate"):
            st.session_state.system_prompt = "You are a helpful pirate assistant named Captain Starlight. You speak with pirate slang, use nautical metaphors, and end sentences with 'Arrr!' when appropriate."
            st.rerun()
    
    with col2:
        if st.button(":material/school: Teacher"):
            st.session_state.system_prompt = "You are Professor Ada, a patient and encouraging teacher. You explain concepts clearly, use examples, and always check for understanding."
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button(":material/mood: Comedian"):
            st.session_state.system_prompt = "You are Chuckles McGee, a witty comedian assistant. You love puns, jokes, and humor, but you're still genuinely helpful. You lighten the mood while providing useful information."
            st.rerun()
    
    with col4:
        if st.button(":material/smart_toy: Robot"):
            st.session_state.system_prompt = "You are UNIT-7, a helpful robot assistant. You speak in a precise, logical manner. You occasionally reference your circuits and processing units."
            st.rerun()
    
    st.divider()
    
    st.text_area(
        "System Prompt:",
        height=200,
        key="system_prompt"
    )
    
    st.divider()

    st.header("Conversation Stats")
    user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
    assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    st.metric("Your Messages", user_msgs)
    st.metric("AI Responses", assistant_msgs)
    
    if st.button("Clear History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Ahoy! Captain Starlight here, ready to help ye navigate the high seas of knowledge! Arrr!"}
        ]
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        def stream_generator():
            conversation = "\n\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in st.session_state.messages
            ])

            full_prompt = f"""{st.session_state.system_prompt}

Here is the conversation so far:
{conversation}

Respond to the user's latest message while staying in character."""
            
            response_text = call_llm(full_prompt)
            for word in response_text.split(" "):
                yield word + " "
                time.sleep(0.02)
        
        with st.spinner("Processing"):
            response = st.write_stream(stream_generator)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

st.divider()
st.caption("Day 13: Adding a System Prompt | 30 Days of AI")