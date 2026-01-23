import streamlit as st

st.title(":material/chat: Chat with Your Documents")
st.write("A conversational RAG chatbot powered by Cortex Search.")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except:
    from snowflake.snowpark import Session
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()

if "doc_messages" not in st.session_state:
    st.session_state.doc_messages = []

with st.sidebar:
    st.header(":material/settings: Settings")

    default_service = st.session_state.get('search_service', 'RAG_DB.RAG_SCHEMA.CUSTOMER_REVIEW_SEARCH')
    
    try:
        services_result = session.sql("SHOW CORTEX SEARCH SERVICES").collect()
        available_services = [f"{row['database_name']}.{row['schema_name']}.{row['name']}" 
                            for row in services_result] if services_result else []
    except:
        available_services = []
    
    if default_service:
        if default_service in available_services:
            available_services.remove(default_service)
        available_services.insert(0, default_service)

    if available_services:
        available_services.append("-- Enter manually --")
        
        search_service_option = st.selectbox(
            "Search Service:",
            options=available_services,
            index=0,
            help="Select your Cortex Search service from Day 19"
        )

        if search_service_option == "-- Enter manually --":
            search_service = st.text_input(
                "Enter service path:",
                placeholder="database.schema.service_name"
            )
        else:
            search_service = search_service_option

            if search_service == st.session_state.get('search_service'):
                st.caption(":material/check_circle: Using service from Day 19")
    else:
        search_service = st.text_input(
            "Cortex Search Service:",
            value=default_service,
            placeholder="database.schema.service_name"
        )
    
    num_chunks = st.slider("Context chunks:", 1, 5, 3,
                           help="Number of relevant chunks to retrieve per question")
    
    st.divider()
    
    if st.button(":material/delete: Clear Chat", use_container_width=True):
        st.session_state.doc_messages = []
        st.rerun()

def search_documents(query, service_path, limit):
    from snowflake.core import Root
    root = Root(session)
    parts = service_path.split(".")
    if len(parts) != 3:
        raise ValueError("Service path must be in format: database.schema.service_name")
    svc = root.databases[parts[0]].schemas[parts[1]].cortex_search_services[parts[2]]
    results = svc.search(query=query, columns=["CHUNK_TEXT", "FILE_NAME"], limit=limit)
    
    chunks_data = []
    for item in results.results:
        chunks_data.append({
            "text": item.get("CHUNK_TEXT", ""),
            "source": item.get("FILE_NAME", "Unknown")
        })
    return chunks_data

if not search_service:
    st.info(":material/arrow_back: Configure a Cortex Search service to start chatting!")
    st.caption(":material/lightbulb: **Need a search service?**\n- Complete Day 19 to create `CUSTOMER_REVIEW_SEARCH`\n- The service will automatically appear in the dropdown above")
else:
    for msg in st.session_state.doc_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about your documents..."):
        st.session_state.doc_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                with st.spinner("Searching and thinking..."):
                    chunks_data = search_documents(prompt, search_service, num_chunks)
                    context = "\n\n---\n\n".join([c["text"] for c in chunks_data])

                    rag_prompt = f"""You are a customer review analysis assistant. Your role is to ONLY answer questions about customer reviews and feedback.

STRICT GUIDELINES:
1. ONLY use information from the provided customer review context below
2. If asked about topics unrelated to customer reviews (e.g., general knowledge, coding, math, news), respond: "I can only answer questions about customer reviews. Please ask about product feedback, customer experiences, or review insights."
3. If the context doesn't contain relevant information, say: "I don't have enough information in the customer reviews to answer that."
4. Stay focused on: product features, customer satisfaction, complaints, praise, quality, pricing, shipping, or customer service mentioned in reviews
5. Do NOT make up information or use knowledge outside the provided reviews

CONTEXT FROM CUSTOMER REVIEWS:
{context}

USER QUESTION: {prompt}

Provide a clear, helpful answer based ONLY on the customer reviews above. If you cite information, mention it naturally."""
                    
                    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{rag_prompt.replace(chr(39), chr(39)+chr(39))}')"
                    response = session.sql(sql).collect()[0][0]
                
                st.markdown(response)

                with st.expander(f":material/library_books: Sources ({len(chunks_data)} reviews used)"):
                    for i, chunk_info in enumerate(chunks_data, 1):
                        st.caption(f"**[{i}] {chunk_info['source']}**")
                        st.write(chunk_info['text'][:200] + "..." if len(chunk_info['text']) > 200 else chunk_info['text'])
                
                st.session_state.doc_messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info(":material/lightbulb: **Troubleshooting:**\n- Make sure the search service exists (check Day 19)\n- Verify the service has finished indexing\n- Check your permissions")

st.divider()
st.caption("Day 22: Chat with Your Documents | 30 Days of AI")