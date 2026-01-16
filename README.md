# MetaKGP Bot
> *The lightning-fast AI guide to IIT Kharagpur.*

## About
MetaKGP Bot is a next-generation RAG chatbot designed to help IIT Kharagpur students navigate campus life. By combining the speed of Groq with the reasoning power of Knowledge Graphs, it answers questions about societies, events, and academic rules instantly.

## Key Features
* **Powered by Groq:** Uses the Groq LPU (Language Processing Unit) for near-instant inference speeds.
* **Hybrid Intelligence:** Combines Google Gemini Embeddings (for factual memory) with open-source models like Llama 3 / Mixtral (via Groq) for reasoning.
* **Graph of Thoughts:** A specialized Logic Layer (NetworkX) that understands hidden connections between campus entities (e.g., Illumination is related to Diwali).
* **Live Wiki Knowledge:** Dynamically retrieves facts from the MetaKGP Wiki.

## Tech Stack
* **LLM Engine:** Groq Cloud (Llama 3 / Mixtral)
* **Embeddings:** Google Gemini (text-embedding-004)
* **Orchestration:** LangChain
* **Vector DB:** FAISS (CPU)
* **Graph Logic:** NetworkX

## Getting Started

### Prerequisites
* Python 3.10+
* Groq API Key (for the Chatbot)
* Google API Key (for the Embeddings/Memory)

### Installation
1. Clone the Repo:
   ```bash
   git clone [https://github.com/abhinav2428/Devso-csecret.git](https://github.com/abhinav2428/Devso-csecret.git)
   cd Devso-csecret
2. Install dependencies:
   pip install -r requirements.txt
3. Set up Credentials: Open the file bot.py and look for the configuration section. You will see placeholder text like PASTE_YOUR_KEY_HERE. Replace that text with your actual API keys:

    GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE"
    GROQ_API_KEY = "PASTE_YOUR_KEY_HERE"
 4.Run the bot:
    python bot.py
