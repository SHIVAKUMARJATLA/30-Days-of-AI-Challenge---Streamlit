import streamlit as st

st.title(":material/chat: Meet the Chat Elements")

with st.chat_message("user"):
    st.write("Hello! Can you explain what Streamlit is?")

with st.chat_message("assistant"):
    st.write("Streamlit is an open-source Python framework for building data apps.")
    st.bar_chart([10, 20, 30, 40]) 

prompt = st.chat_input("Type a message here...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        st.write(f"You just said:\n\n '{prompt}' \n\n(I don't have memory yet!)")

st.divider()
st.caption("Day 8: Meet the Chat Elements | 30 Days of AI")