import os
import json
import networkx as nx
from typing import List, Dict
from langchain_community.vectorstores import FAISS
#from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq

# ==============================================================================
# SECURE KEY LOADING: Load the hidden keys from the .env file
# ==============================================================================
from dotenv import load_dotenv
load_dotenv() # This automatically grabs the keys from your .env file

# Now os.getenv will successfully find your keys without them being hardcoded!
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# The Router: A fast, lightweight model used exclusively to classify the intent
router_llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, temperature=0.5)

# The Experts: Distinct models optimized for specific domains
expert_llms = {
    # Heavy reasoning for complex logic and rules
    "ACADEMIC": ChatGroq(model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, temperature=0.1), 
    # Broad/creative contexts for student life
    "CLUB": ChatGroq(model_name="mixtral-8x7b-32768", api_key=GROQ_API_KEY, temperature=0.4),          
    # Fast, factual extraction for locations and buildings
    "INFRASTRUCTURE": ChatGroq(model_name="llama-3.1-8b-instant", api_key=GROQ_API_KEY, temperature=0.1)       
}

def moe_route(query: str) -> str:
    """
    Routes the query to the correct domain category.
    Returns the string key used to fetch the physical LLM from expert_llms.
    """
    prompt = f"""
    Classify the query into ONE category: ACADEMIC, CLUB, or INFRASTRUCTURE.
    Query: {query}
    Output ONLY the category word.
    """
    # Ask the router model to classify the query
    category = router_llm.invoke(prompt).content.strip().upper()
    
    # Safe fallback: If the router hallucinates an invalid category, 
    # default to the heaviest reasoning model (ACADEMIC) to prevent a KeyError crash.
    return category if category in expert_llms else "ACADEMIC"


# =====================================================================
# 2. GRAPH OF THOUGHTS (GoT) ENGINE
# =====================================================================
# Manages thoughts as an independent graph structure in memory, executing
# Generate, Evaluate, Refine, and Aggregate operations.

class Thought:
    """Represents a single node of reasoning within the GoT engine."""
    def __init__(self, id: str, content: str, parents: List[str] = None):
        self.id = id
        self.content = content
        self.parents = parents or []
        self.score = 0.0
        self.verified = False

class GraphOfThoughts:
    """Executes GoT operations using a designated Expert LLM."""
    def __init__(self, expert_llm, vector_context: str, graph_context: str):
        self.llm = expert_llm
        self.v_context = vector_context
        self.g_context = graph_context
        self.thoughts: Dict[str, Thought] = {}
        self.thought_counter = 0

    def _get_id(self):
        """Helper to generate unique IDs for new thoughts."""
        self.thought_counter += 1
        return f"t_{self.thought_counter}"

    def generate(self, sub_question: str, num_branches: int = 3) -> List[str]:
        """GoT Operation 1: Branching (Generates multiple independent thoughts)"""
        prompt = f"""
        Question: {sub_question}
        Vector Context: {self.v_context}
        Graph Context: {self.g_context}
        
        Generate {num_branches} different possible answers or reasoning paths based ONLY on context.
        Separate each distinct thought strictly with "|||".
        """
        response = self.llm.invoke(prompt).content
        raw_thoughts = [t.strip() for t in response.split("|||") if t.strip()]
        
        thought_ids = []
        for content in raw_thoughts:
            tid = self._get_id()
            # Store the generated thought in the graph dictionary
            self.thoughts[tid] = Thought(id=tid, content=content)
            thought_ids.append(tid)
        return thought_ids

    def evaluate(self, thought_ids: List[str]) -> None:
        """GoT Operation 2: Evaluation (Scores thoughts against vector/graph context)"""
        for tid in thought_ids:
            thought = self.thoughts[tid]
            prompt = f"""
            Rate this claim based on the provided contexts from 0 to 10.
            Claim: {thought.content}
            Context: {self.v_context} | {self.g_context}
            Output ONLY the integer score.
            """
            try:
                # Extract the integer score from the LLM's response
                score_str = self.llm.invoke(prompt).content.strip()
                thought.score = float(''.join(filter(str.isdigit, score_str)))
            except:
                thought.score = 0.0
            
            # Mark as verified if the score meets the strict threshold
            thought.verified = thought.score >= 7.0

    def refine(self, thought_ids: List[str]) -> List[str]:
        """GoT Operation 3: Refinement (Improves low-scoring 'almost right' thoughts)"""
        refined_ids = []
        for tid in thought_ids:
            thought = self.thoughts[tid]
            # Only attempt to refine thoughts that have some merit but aren't perfect
            if 3.0 <= thought.score < 7.0: 
                prompt = f"""
                This thought is partially incorrect based on the context. Fix it.
                Thought: {thought.content}
                Context: {self.v_context} | {self.g_context}
                Output ONLY the corrected thought.
                """
                new_content = self.llm.invoke(prompt).content.strip()
                new_tid = self._get_id()
                # Create a new thought node, linking it to its parent thought
                self.thoughts[new_tid] = Thought(id=new_tid, content=new_content, parents=[tid])
                refined_ids.append(new_tid)
        return refined_ids

    def aggregate(self, thought_ids: List[str]) -> str:
        """GoT Operation 4: Aggregation (Merges the best paths together)"""
        valid_thoughts = [self.thoughts[tid] for tid in thought_ids if self.thoughts[tid].verified]
        
        if not valid_thoughts:
            return "Information missing or unverifiable."
            
        if len(valid_thoughts) == 1:
            return valid_thoughts[0].content
            
        # Merge multiple valid perspectives into one comprehensive super-thought
        combined_content = "\n".join([f"- {t.content}" for t in valid_thoughts])
        prompt = f"""
        Merge these valid, overlapping thoughts into one concise, comprehensive answer:
        {combined_content}
        """
        final_content = self.llm.invoke(prompt).content.strip()
        
        # Save the aggregated final thought back to the internal graph
        agg_tid = self._get_id()
        self.thoughts[agg_tid] = Thought(id=agg_tid, content=final_content, parents=[t.id for t in valid_thoughts])
        self.thoughts[agg_tid].verified = True
        
        return final_content


# =====================================================================
# 3. KNOWLEDGE RETRIEVAL & ORCHESTRATION
# =====================================================================

print("Initializing FAISS Vector Database...")
# Initialize the Google embedding model for semantic search
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")  
vector_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

print("Initializing NetworkX Knowledge Graph...")
# Load the pre-built NetworkX graph, or create an empty directed graph if missing
try:
    G = nx.read_gml("metakgp_graph.gml")
except:
    G = nx.DiGraph()

def get_graph_context(query: str) -> str:
    """Performs 1-Hop traversal on the NetworkX knowledge graph."""
    query_lower = query.lower()
    related_nodes = []
    
    if G.number_of_nodes() > 0:
        for node in G.nodes():
            # Clean the URL to match against the query string
            node_title = node.split('/')[-1].replace('_', ' ').lower()
            if node_title in query_lower:
                # Traverse exactly one hop outward to pull related explicit entities
                neighbors = list(G.successors(node)) if G.is_directed() else list(G.neighbors(node))
                related_nodes.extend(neighbors[:5])
    
    if related_nodes:
        clean_names = [n.split('/')[-1].replace('_', ' ') for n in related_nodes]
        return f"Explicit Graph Relationships: {', '.join(clean_names)}"
    return "No explicit graph connections found."

def planner_agent(query: str) -> List[str]:
    """Decomposes the main query into sub-questions using the fast router model."""
    prompt = f"""
    Break this query into simple, searchable sub-questions. 
    Expand acronyms (e.g., TFPS -> Technology Film and Photography Society).
    Query: {query}
    Output ONLY a valid JSON list of strings.
    """
    try:
        response = router_llm.invoke(prompt).content
        start = response.find('[')
        end = response.rfind(']') + 1
        return json.loads(response[start:end])
    except:
        return [query]

def generate_response_true_got(query: str) -> str:
    """Orchestrates the entire end-to-end GoT and MoE pipeline."""
    plan = planner_agent(query)
    final_verified_facts = []

    for sub_question in plan:
        # Phase 1: Context Retrieval (Vector + Graph)
        retriever = vector_db.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(sub_question)
        v_context = "\n".join([d.page_content for d in docs])
        g_context = get_graph_context(sub_question)
        
        # Phase 2: MoE Routing (Select the appropriate physical LLM)
        category = moe_route(sub_question)
        expert_llm = expert_llms[category]
        
        # Phase 3: GoT Execution Pipeline
        got_engine = GraphOfThoughts(expert_llm=expert_llm, vector_context=v_context, graph_context=g_context)
        
        # 3a. Generate (Branch)
        t_ids = got_engine.generate(sub_question, num_branches=3)
        
        # 3b. Evaluate (Score)
        got_engine.evaluate(t_ids)
        
        # 3c. Refine (Loop back to fix flawed thoughts)
        refined_t_ids = got_engine.refine(t_ids)
        if refined_t_ids:
            got_engine.evaluate(refined_t_ids) 
            t_ids.extend(refined_t_ids)
            
        # 3d. Aggregate (Merge surviving thoughts)
        best_answer = got_engine.aggregate(t_ids)
        
        final_verified_facts.append(f"- {best_answer} (Source: {category} Expert)")

        # Phase 4: Dynamic Knowledge Graph Update
        # Persist valid logical steps back into the global NetworkX graph
        if "missing" not in best_answer.lower():
            G.add_node(sub_question, label="Validated_Thought", answer=best_answer)

    # Phase 5: Final Synthesis
    # Hard-routed to the 70B Academic model for superior structural coherence
    synthesis_prompt = f"""
    User Query: {query}
    Verified Facts:
    {chr(10).join(final_verified_facts)}
    Construct a coherent final answer using ONLY these facts.
    """
    return expert_llms["ACADEMIC"].invoke(synthesis_prompt).content


# =====================================================================
# 4. START CHATTING CLI
# =====================================================================
if __name__ == "__main__":
    print("\nGraphMind BOT IS READY! (Type 'exit' to stop)")
    while True:
        q = input("\nYou: ")
        if q.lower() in ["exit", "quit"]:
            break
        
        try:
            response = generate_response_true_got(q)
            print(f"\nBot: {response}")
        except Exception as e:
            print(f"Error: {e}")