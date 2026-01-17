# MetaKGP Wiki Scraper & Vector Database

A Python project that scrapes the MetaKGP wiki, processes article content, and builds a searchable vector database using Google's Generative AI embeddings and FAISS.

## Overview

This project automates the extraction of knowledge from the MetaKGP wiki and creates a vector database for semantic search capabilities. It works in three main stages:

1. **URL Discovery** - Fetch all article URLs from the MetaKGP API
2. **Content Extraction** - Download and process article content from the wiki
3. **Vectorization** - Create embeddings and build a FAISS vector index using Google's API

## Features

- ✅ Automated wiki scraping via MetaKGP API
- ✅ HTML content cleaning and text extraction
- ✅ Batch processing with configurable sizes
- ✅ Knowledge graph generation using NetworkX
- ✅ Cloud-based embedding generation with Modal
- ✅ FAISS vector database for semantic search
- ✅ Graceful error handling and progress logging

## Requirements

- Python 3.8+
- Internet connection (for API calls)
- Google Generative AI API key
- Modal account (for cloud ingestion)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd devsoc-2
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
   - Get your Google Generative AI API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - For Modal deployment, install and configure Modal CLI:
   ```bash
   pip install modal
   modal token new
   ```

## Usage

### Step 1: Fetch Article URLs

Run `main.py` to discover all articles from the MetaKGP wiki:

```bash
python main.py
```

**Output:** Creates `all_article_urls.txt` with one URL per line.

### Step 2: Fetch and Process Content

Run `fetch_content.py` to download article content and structure:

```bash
python fetch_content.py
```

**Configuration:**
- `INPUT_FILE`: Input URL file (default: `all_article_urls.txt`)
- `OUTPUT_DIR`: Output directory for batch files (default: `metakgp_data`)
- `BATCH_SIZE`: Number of pages per batch file (default: 100)

**Output:** Creates JSON files in `metakgp_data/` with:
- `url`: Article URL
- `title`: Article title
- `content`: Cleaned article content
- `links`: Outgoing wiki links

### Step 3: Create Vector Database (Cloud)

Run `ingest_modal.py` to create embeddings and FAISS index on Modal cloud:

```bash
# Update MY_API_KEY in ingest_modal.py with your Google API key
python ingest_modal.py
```

**Note:** This requires a Modal account. The script:
1. Processes all JSON files in `metakgp_data/`
2. Creates embeddings using Google Generative AI
3. Builds FAISS index for semantic search
4. Generates knowledge graph in GML format
5. Downloads results as `results.zip`

**Output files:**
- `faiss_index/` - FAISS vector database
- `metakgp_graph.gml` - Knowledge graph in GML format

## Project Structure

```
.
├── main.py                      # Fetch all wiki article URLs
├── fetch_content.py             # Download and process article content
├── ingest_modal.py              # Cloud ingestion with Google embeddings
├── bot.py                       # Bot implementation (if applicable)
├── families/
│   └── metakgp_family.py        # PyWikiBot family configuration
├── metakgp_data/                # Generated batch JSON files
├── faiss_index/                 # Generated FAISS vector index
├── all_article_urls.txt         # Generated URL list
├── metakgp_graph.gml            # Generated knowledge graph
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Configuration

### main.py
- `API_URL`: MetaKGP API endpoint (default: `https://wiki.metakgp.org/api.php`)
- `OUTPUT_FILE`: Output file for URLs (default: `all_article_urls.txt`)
- `BASE_URL`: Wiki base URL (default: `https://wiki.metakgp.org/wiki/`)

### fetch_content.py
- `INPUT_FILE`: Input URL file
- `OUTPUT_DIR`: Output directory for batch data
- `BATCH_SIZE`: Pages to accumulate before saving
- `API_URL`: MetaKGP API endpoint
- `User-Agent`: Browser identification string

### ingest_modal.py
- `MY_API_KEY`: Google Generative AI API key (⚠️ **Keep this secret!**)
- `chunk_size`: Text chunk size for embeddings (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `embedding_model`: Google embedding model (default: `models/text-embedding-004`)

## API Keys & Credentials

⚠️ **Security Warning:**
- Never commit API keys to the repository
- Use environment variables for sensitive data
- Add `.env` file to `.gitignore`

### Secure Setup

Create a `.env` file (not tracked by git):
```
GOOGLE_API_KEY=your_api_key_here
```

Then update scripts to load from environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()
MY_API_KEY = os.getenv("GOOGLE_API_KEY")
```

## Dependencies

- `requests` - HTTP client for API calls
- `beautifulsoup4` - HTML parsing and cleaning
- `langchain` - LLM framework
- `langchain-google-genai` - Google embeddings integration
- `langchain-text-splitters` - Text chunking
- `faiss-cpu` - Vector similarity search
- `networkx` - Graph data structure
- `modal` - Cloud compute platform
- `pywikibot` - Wiki API interaction (optional)

Install all with:
```bash
pip install -r requirements.txt
```

## Error Handling

The scripts include robust error handling:
- Network timeouts (10-second timeout)
- API error responses
- File I/O errors
- Encoding issues (UTF-8 handling)

Check console output for detailed error messages and logs.

## Performance Tips

1. **Batch Size**: Adjust `BATCH_SIZE` in `fetch_content.py` based on your system:
   - Smaller batches (10-50) for slow connections
   - Larger batches (200-500) for high-speed connections

2. **Rate Limiting**: `fetch_content.py` includes 0.1s delay per request to be polite to the wiki server

3. **Cloud Ingestion**: Modal cloud handles parallel processing for faster embedding generation

## Troubleshooting

### "Error: all_article_urls.txt not found!"
- Run `main.py` first to generate the URL list

### "API Error: Page not found"
- Some wiki pages may have been deleted or redirected
- Check the page exists at `https://wiki.metakgp.org/wiki/PageName`

### "FAISS import error"
- Reinstall: `pip install --force-reinstall faiss-cpu`

### "Google API key error"
- Verify API key is correct and has Generative AI access
- Check API key in `ingest_modal.py` line with `MY_API_KEY`

### "Modal authentication failed"
- Run `modal token new` to set up Modal credentials
- Ensure Modal CLI is installed: `pip install modal`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here, e.g., MIT, Apache 2.0, etc.]

## Contact & Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

**Note:** This project is designed for the MetaKGP wiki. Adaptation to other wikis may require configuration changes.
