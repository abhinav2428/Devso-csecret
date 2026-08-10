import streamlit as st

# ==============================================================================
# 1. IMPORT YOUR ACTUAL BACKEND
# This imports the main orchestration function directly from your bot.py file.
# Because FAISS and the LLMs are initialized globally in bot.py, they will load
# automatically the moment this import runs.
# ==============================================================================
from bot import generate_response_true_got 

# ==============================================================================
# 2. STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="GraphMind Agent",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 GraphMind Agent")
st.markdown("Powered by FAISS, NetworkX, and Mixture of Experts (MoE)")

# ==============================================================================
# 3. CHAT HISTORY STATE MANAGEMENT
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==============================================================================
# 4. USER INPUT AND EXECUTION
# ==============================================================================
if prompt := st.chat_input("Ask a complex question requiring thought aggregation..."):
    
    # Render user query
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Execute GraphMind pipeline
    with st.chat_message("assistant"):
        with st.spinner("Decomposing query, retrieving from FAISS, and aggregating thoughts..."):
            
            try:
                # Call the true GoT function from bot.py
                response = generate_response_true_got(prompt)
                st.markdown(response)
            except Exception as e:
                # Catch any API or database errors gracefully
                response = f"**Error executing GraphMind pipeline:** {str(e)}"
                st.error(response)
            
    # Save response to history
    st.session_state.messages.append({"role": "assistant", "content": response})