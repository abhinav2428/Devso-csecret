import os
import networkx as nx
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# --- CONFIGURATION ---
#  PASTE YOUR API KEY HERE
GOOGLE_API_KEY = "AIzaSyAsgcIwteMXQzve95ki1gTeIMMlq7zGGo8"

VECTOR_DB_DIR = "faiss_index"
GRAPH_FILE = "metakgp_graph.gml"

# 1. SETUP BRAINS 
print("Loading Google Embeddings...")
# We use the same model name as we did in the cloud
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=GOOGLE_API_KEY
)

print("Loading Vector DB (Facts)...")
try:
    vector_db = FAISS.load_local(
        VECTOR_DB_DIR, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    print("Vector DB loaded!")
except Exception as e:
    print(f"Error loading Vector DB: {e}")
    exit()

print("Loading Graph (Logic)...")
G = nx.read_gml(GRAPH_FILE)

print("Initializing Gemini...")
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", 
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# 2. HELPER FUNCTIONS
def get_graph_context(query):
    query = query.lower()
    related_nodes = []
    for node in G.nodes():
        if node.lower() in query:
            neighbors = list(G.neighbors(node))
            related_nodes.extend(neighbors[:5])
    
    if related_nodes:
        clean_names = [n.split('/')[-1].replace('_', ' ') for n in related_nodes]
        return f"Related topics: {', '.join(clean_names)}"
    return "No direct connections found."

def generate_response(query):
    # A. Retrieve Facts
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    context_text = "\n\n".join([d.page_content for d in docs])
    
    # B. Get Graph Info
    graph_info = get_graph_context(query)
    
    # C. Ask Gemini
    prompt = f"""
    You are a helpful assistant for IIT Kharagpur (MetaKGP).
    
    CONTEXT FROM GRAPH:
    {graph_info}
    
    FACTS FROM WIKI:
    {context_text}
    
    USER QUESTION: {query}
    
    Answer the question using the facts above. If you don't know, say so.
    """
    return llm.invoke(prompt).content

# 3. START CHATTING
print("\n BOT IS READY! (Type 'exit' to stop)")
while True:
    q = input("\nYou: ")
    if q.lower() in ["exit", "quit"]:
        break
    
    print("Bot thinking...")
    try:
        response = generate_response(q)
        print(f" Bot: {response}")
    except Exception as e:
        print(f" Error: {e}")