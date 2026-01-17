# MetaKGP RAG Bot - Frontend Integration Guide

## 📋 Overview

Your RAG bot now has a complete web interface with:
- **Modern Chat UI** - Clean, responsive interface
- **Flask Backend API** - REST API wrapping your bot.py
- **Real-time Communication** - WebSocket-ready architecture
- **History & Settings** - Persistent conversation history
- **Status Monitoring** - API health checks

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd "c:\Users\Admin\Desktop\DEVSOCSECRET\Devso-csecret\devsoc 2"
pip install -r requirements.txt
```

### Step 2: Run the Backend Server

```bash
python app.py
```

You should see:
```
============================================================
MetaKGP RAG Bot - Flask API Server
============================================================
Loading bot components...
Vector DB: ✓ Loaded
Graph: ✓ Loaded
============================================================

Starting server on http://127.0.0.1:5000
Frontend: http://127.0.0.1:5000
API: http://127.0.0.1:5000/api

Press Ctrl+C to stop the server
```

### Step 3: Open Frontend in Browser

Open your browser and go to: **http://127.0.0.1:5000**

## 📁 Project Structure

```
devsoc 2/
├── app.py                    # Flask backend server
├── bot.py                    # Your original RAG bot (unchanged)
├── static/
│   ├── index.html           # Chat UI
│   ├── styles.css           # Styling
│   └── script.js            # Frontend logic
├── requirements.txt         # Dependencies
├── faiss_index/             # Vector DB
├── metakgp_graph.gml        # Knowledge graph
└── metakgp_data/            # Training data
```

## 🔌 API Endpoints

### 1. **POST /api/chat**
Send a message to the bot

**Request:**
```json
{
    "message": "Who is the VP of TFPS?"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Based on the verified sources...",
    "timestamp": "2025-01-17T10:30:00.000Z",
    "message_count": 5
}
```

### 2. **GET /api/status**
Check bot and API status

**Response:**
```json
{
    "success": true,
    "bot_status": "ready",
    "vector_db_loaded": true,
    "graph_loaded": true,
    "conversation_count": 3,
    "timestamp": "2025-01-17T10:30:00.000Z"
}
```

### 3. **GET /api/history**
Get conversation history

**Query Parameters:**
- `limit` (optional): Number of messages to retrieve (default: 20)

**Response:**
```json
{
    "success": true,
    "history": [
        {
            "timestamp": "2025-01-17T10:25:00.000Z",
            "user": "Who is the VP of TFPS?",
            "bot": "The Vice President of TFPS is..."
        }
    ],
    "total": 5
}
```

### 4. **POST /api/clear**
Clear all conversation history

**Response:**
```json
{
    "success": true,
    "message": "History cleared"
}
```

### 5. **GET /api/health**
Health check endpoint

**Response:**
```json
{
    "status": "healthy",
    "service": "MetaKGP RAG Bot API",
    "timestamp": "2025-01-17T10:30:00.000Z"
}
```

## 🎨 Frontend Features

### Chat Interface
- ✅ Real-time message sending
- ✅ Auto-scrolling to latest message
- ✅ Typing indicator
- ✅ Timestamp for each message
- ✅ Verification badges (MoE Expert verification)

### Sidebar
- ✅ New chat button
- ✅ Conversation history
- ✅ Settings
- ✅ API status indicator

### History Modal
- ✅ View past conversations
- ✅ Quick re-use of previous queries
- ✅ Timestamps
- ✅ Clear history option

### Settings Modal
- ✅ API status monitoring
- ✅ Theme selection (Light/Dark/Auto)
- ✅ Response detail level

## 🔧 Configuration

### Change Port

Edit `app.py` line at the bottom:
```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)  # Change 5000 to your port
```

### Change Host

To allow external connections:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Disable Debug Mode

For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

Create a `.env` file:
```
FLASK_ENV=production
FLASK_DEBUG=0
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

## 🐛 Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Vector DB not loading

**Solution:** Make sure `faiss_index` folder exists with `index.faiss` file.
If not, run:
```bash
python ingest_modal.py
```

### Issue: Bot taking too long to respond

**Info:** The MoE verification system with 3 experts takes time. This is normal.
Each query:
1. Generates multiple reasoning paths
2. Evaluates with 3 expert systems
3. Ranks and selects best answer

### Issue: Port 5000 already in use

**Solution:** Change the port in `app.py` or kill the process using it:
```bash
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📊 How It Works

```
User Query
    ↓
[Frontend] HTML/CSS/JS Interface
    ↓ (HTTP POST /api/chat)
[Backend] Flask API (app.py)
    ↓
[Bot Core] Graph of Thoughts Engine (bot.py)
    ↓
1. Planning Agent (Decompose query)
    ↓
2. Execution Agent (Multiple reasoning paths)
    ↓
3. MoE Verification (3 Expert Consensus)
    ├─ Source Matcher
    ├─ Hallucination Hunter
    └─ Logic Expert
    ↓
4. Synthesis Agent (Final answer with citations)
    ↓
[Database] Vector DB + Knowledge Graph
    ↓
Response sent back to Frontend
```

## 🎯 Advanced Usage

### Custom API Integration

```javascript
// In your own app
fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
        message: 'Who is the president of TSG?' 
    })
})
.then(r => r.json())
.then(data => console.log(data.response));
```

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t metakgp-bot .
docker run -p 5000:5000 metakgp-bot
```

## 📝 Next Steps

1. ✅ Backend API created
2. ✅ Frontend UI created
3. ✅ Integration complete
4. 🔲 Deploy to cloud (Heroku, AWS, etc.)
5. 🔲 Add more data sources
6. 🔲 Implement user authentication
7. 🔲 Add analytics/logging

## 💡 Tips

- The bot automatically saves conversation history
- All responses are verified by MoE experts
- The system learns and updates the knowledge graph
- Check `/api/status` to monitor health
- Use `/api/history` to audit conversations

## 🤝 Support

For issues, check:
1. Console output in Flask terminal
2. Browser DevTools (F12) JavaScript console
3. Network tab for API requests

---

**Happy chatting! 🎉**
