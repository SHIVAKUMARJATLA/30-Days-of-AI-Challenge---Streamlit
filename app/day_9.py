import streamlit as st

st.title(":material/memory: Understanding Session State")

st.warning("**Instructions:** Try clicking the + and - buttons in both columns to see the difference.")

col1, col2 = st.columns(2)

with col1:
    st.header(":material/cancel: Standard Variable")
    st.write("This resets on every click.")

    count_wrong = 0
    
    subcol_left, subcol_right = st.columns(2)
    
    with subcol_left:
        if st.button(":material/add:", key="std_plus"):
            count_wrong += 1

    with subcol_right:
        if st.button(":material/remove:", key="std_minus"):
            count_wrong -= 1
    
    st.metric("Standard Count", count_wrong)
    st.caption("It never gets past 1 or -1 because `count_wrong` resets to 0 before the math happens.")

with col2:
    st.header(":material/check_circle: Session State")
    st.write("This memory persists.")

    if "counter" not in st.session_state:
        st.session_state.counter = 0
    
    subcol_left_2, subcol_right_2 = st.columns(2)

    with subcol_left_2:
        if st.button(":material/add:", key="state_plus"):
            st.session_state.counter += 1

    with subcol_right_2:
        if st.button(":material/remove:", key="state_minus"):
            st.session_state.counter -= 1

    st.metric("State Count", st.session_state.counter)
    st.caption("This works because we only set the counter to 0 if it doesn't exist.")

st.divider()
st.caption("Day 9: Understanding Session State | 30 Days of AI")