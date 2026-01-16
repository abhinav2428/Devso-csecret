# import os
# import networkx as nx
# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_groq import ChatGroq
# # --- CONFIGURATION ---
# #  PASTE YOUR API KEY HERE
# GOOGLE_API_KEY = "AIzaSyAsgcIwteMXQzve95ki1gTeIMMlq7zGGo8"
# GROQ_API_KEY = "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"
# VECTOR_DB_DIR = "faiss_index"
# GRAPH_FILE = "metakgp_graph.gml"

# # 1. SETUP BRAINS 
# print("Loading Google Embeddings...")
# # We use the same model name as we did in the cloud
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/text-embedding-004", 
#     google_api_key=GOOGLE_API_KEY
# )

# print("Loading Vector DB (Facts)...")
# try:
#     vector_db = FAISS.load_local(
#         VECTOR_DB_DIR, 
#         embeddings, 
#         allow_dangerous_deserialization=True
#     )
#     print("Vector DB loaded!")
# except Exception as e:
#     print(f"Error loading Vector DB: {e}")
#     exit()

# print("Loading Graph (Logic)...")
# G = nx.read_gml(GRAPH_FILE)

# print("Initializing Gemini...")
# llm = ChatGoogleGenerativeAI(
#     model="gemini-pro", 
#     google_api_key=GOOGLE_API_KEY,
#     temperature=0.3
# )

# # 2. HELPER FUNCTIONS
# def get_graph_context(query):
#     query = query.lower()
#     related_nodes = []
#     for node in G.nodes():
#         if node.lower() in query:
#             neighbors = list(G.neighbors(node))
#             related_nodes.extend(neighbors[:5])
    
#     if related_nodes:
#         clean_names = [n.split('/')[-1].replace('_', ' ') for n in related_nodes]
#         return f"Related topics: {', '.join(clean_names)}"
#     return "No direct connections found."

# def generate_response(query):
#     # A. Retrieve Facts
#     retriever = vector_db.as_retriever(search_kwargs={"k": 3})
#     docs = retriever.invoke(query)
#     context_text = "\n\n".join([d.page_content for d in docs])
    
#     # B. Get Graph Info
#     graph_info = get_graph_context(query)
    
#     # C. Ask Gemini
#     prompt = f"""
#     You are a helpful assistant for IIT Kharagpur (MetaKGP).
    
#     CONTEXT FROM GRAPH:
#     {graph_info}
    
#     FACTS FROM WIKI:
#     {context_text}
    
#     USER QUESTION: {query}
    
#     Answer the question using the facts above. If you don't know, say so.
#     """
#     return llm.invoke(prompt).content

# # 3. START CHATTING
# print("\n BOT IS READY! (Type 'exit' to stop)")
# while True:
#     q = input("\nYou: ")
#     if q.lower() in ["exit", "quit"]:
#         break
    
#     print("Bot thinking...")
#     try:
#         response = generate_response(q)
#         print(f" Bot: {response}")
#     except Exception as e:
#         print(f" Error: {e}")
import os
import networkx as nx
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# 1. NEW IMPORT: Groq
from langchain_groq import ChatGroq

# --- GRAPH OF THOUGHTS ENGINE ---

class ThoughtNode:
    def __init__(self, id, question):
        self.id = id
        self.question = question
        self.retrieved_context = ""
        self.derived_thought = ""
        self.verified = False
        self.score = 0

def planner_agent(query):
    """
    Step 1: DECOMPOSITION
    Breaks the user query into a logical dependency graph (list of steps).
    """
    system_prompt = """
    You are a Planning Agent. Break the user's complex query into small, searchable sub-questions.
    Return ONLY a JSON list of strings.
    Example: ["Who is the governor?", "When was the society established?"]
    """
    prompt = f"User Query: {query}\n\nPlan:"
    
    # We ask Llama 3 to give us a JSON plan
    response = llm.invoke([("system", system_prompt), ("human", prompt)]).content
    
    # Clean the response to ensure it's valid JSON
    try:
        # Sometimes LLMs add text around the JSON, we try to strip it
        start = response.find('[')
        end = response.rfind(']') + 1
        plan = json.loads(response[start:end])
        return plan
    except:
        return [query] # Fallback: Just treat the original query as the only step

def execution_agent(node, vector_db, graph_context):
    # Retrieve
    retriever = vector_db.as_retriever(search_kwargs={"k": 5}) # Fetch top 5 chunks
    docs = retriever.invoke(node.question)
    
    # --- DEBUGGING START ---
    print(f"\n[DEBUG] Searching for: '{node.question}'")
    print(f"[DEBUG] Found {len(docs)} chunks.")
    for i, doc in enumerate(docs):
        print(f"--- Chunk {i+1} ---")
        print(doc.page_content[:300]) # Print first 300 characters
        print("------------------")
    # --- DEBUGGING END ---
    
    context_text = "\n".join([d.page_content for d in docs])
    # ... rest of code ...
def verification_agent(node):
    """
    Step 3: MoE VERIFICATION (The "Judge")
    Checks if the thought is supported by the context.
    """
    prompt = f"""
    You are a strict Hallucination Hunter.
    
    Claim: {node.derived_thought}
    Source Text: {node.retrieved_context}
    
    Does the Source Text explicitly support the Claim? 
    Reply with ONLY 'YES' or 'NO'.
    """
    verdict = llm.invoke(prompt).content.strip().upper()
    
    if "YES" in verdict:
        node.verified = True
        node.score = 10
    else:
        node.verified = False
        node.score = 0
        node.derived_thought = "(Unverified info discarded)"
    
    return node

def synthesis_agent(original_query, nodes):
    """
    Step 4: AGGREGATION
    Combines all verified thoughts into the final answer.
    """
    verified_facts = "\n".join([f"- {n.derived_thought}" for n in nodes if n.verified])
    
    prompt = f"""
    User Query: {original_query}
    
    Verified Facts gathered by researchers:
    {verified_facts}
    
    Construct a coherent, helpful final answer using these facts.
    Cite your sources if possible.
    """
    return llm.invoke(prompt).content

# --- MAIN ORCHESTRATOR ---

def generate_response_got(query):
    print(f" [GoT] 1. Planning: Analyzing '{query}'...")
    plan = planner_agent(query)
    print(f" [GoT]    Plan: {plan}")
    
    nodes = []
    
    # Execute the Graph (Sequential for now, can be parallelized)
    for i, sub_question in enumerate(plan):
        print(f" [GoT] 2. Executing Step {i+1}: {sub_question}")
        
        # Create Node
        node = ThoughtNode(id=i, question=sub_question)
        
        # Get Graph Context (using your existing function)
        g_context = get_graph_context(sub_question)
        
        # Retrieve & Think
        node = execution_agent(node, vector_db, g_context)
        
        # Verify (The MoE Check)
        node = verification_agent(node)
        print(f" [GoT] 3. Verification Score: {node.score}/10")
        
        nodes.append(node)
    
    print(f" [GoT] 4. Synthesizing Final Answer...")
    final_answer = synthesis_agent(query, nodes)
    return final_answer


# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyAsgcIwteMXQzve95ki1gTeIMMlq7zGGo8" # Keep this for Embeddings
GROQ_API_KEY = "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"     # Paste your new gsk_... key here

VECTOR_DB_DIR = "faiss_index"
GRAPH_FILE = "metakgp_graph.gml"

# 2. SETUP BRAINS 
print("Loading Google Embeddings...")
# We keep Google for embeddings because your DB is already built with it!
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
    # Tip: If this fails, run 'python ingest_modal.py' again
    exit()

print("Loading Graph (Logic)...")
try:
    G = nx.read_gml(GRAPH_FILE)
except:
    print("Warning: Graph file not found. Graph features will be skipped.")
    G = nx.Graph()

print("Initializing Groq (Llama 3)...")
# 3. CHANGE: Switch from Gemini to Groq
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile"
    
    
    ,  # A very powerful, fast model
    api_key=GROQ_API_KEY,
    temperature=0.3
)

# 4. HELPER FUNCTIONS
def get_graph_context(query):
    query = query.lower()
    related_nodes = []
    # Simple check to prevent errors if graph is empty
    if G.number_of_nodes() > 0:
        for node in G.nodes():
            if node.lower() in query:
                neighbors = list(G.neighbors(node))
                related_nodes.extend(neighbors[:5])
    
    if related_nodes:
        clean_names = [n.split('/')[-1].replace('_', ' ') for n in related_nodes]
        return f"Related topics: {', '.join(clean_names)}"
    return "No direct connections found."

def generate_response_got(query):
    print(f" [GoT] 1. Planning: Analyzing '{query}'...")
    plan = planner_agent(query)
    print(f" [GoT]    Plan: {plan}")
    
    nodes = []
    
    # Execute the Graph
    for i, sub_question in enumerate(plan):
        print(f" [GoT] 2. Executing Step {i+1}: {sub_question}")
        
        node = ThoughtNode(id=i, question=sub_question)
        g_context = get_graph_context(sub_question)
        node = execution_agent(node, vector_db, g_context)
        node = verification_agent(node)
        
        print(f" [GoT] 3. Verification Score: {node.score}/10")
        nodes.append(node)

        # --- NEW CODE: DYNAMIC GRAPH UPDATE ---
        # Only add to graph if it's VERIFIED and useful (not "I don't know")
        if node.verified and "I don't know" not in node.derived_thought:
            print(f" [Graph] Learning new fact: {node.question}...")
            
            # 1. Add the Node (The Sub-Question)
            # We store the answer as a property of the node
            G.add_node(node.question, label="Thought", answer=node.derived_thought)
            
            # 2. Add the Edge (Connect it to the main topic)
            # We try to link it to the main query terms if they exist in the graph
            # Or just link to the previous node to show a "chain of thought"
            if i > 0:
                prev_node = nodes[i-1]
                G.add_edge(prev_node.question, node.question, relation="leads_to")
            
            # 3. SAVE TO DISK (Persistence)
            try:
                nx.write_gml(G, GRAPH_FILE)
                print(" [Graph] Memory updated on disk.")
            except Exception as e:
                print(f" [Graph] Warning: Could not save graph: {e}")
        # --------------------------------------
    
    print(f" [GoT] 4. Synthesizing Final Answer...")
    final_answer = synthesis_agent(query, nodes)
    return final_answer

# 5. START CHATTING
print("\nBOT IS READY! (Type 'exit' to stop)")
while True:
    q = input("\nYou: ")
    if q.lower() in ["exit", "quit"]:
        break
    
    try:
        # CHANGED: Now calling the Graph of Thoughts function
        response = generate_response_got(q)
        print(f"\nBot: {response}")
    except Exception as e:
        print(f"Error: {e}")