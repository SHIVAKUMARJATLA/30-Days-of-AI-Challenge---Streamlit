import streamlit as st
st.title("❄️ Day 1: Streamlit + Snowflake")
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()

version = session.sql("SELECT CURRENT_VERSION()").collect()[0][0]
st.success(f"Successfully connected! SNowflake Version: {version}")