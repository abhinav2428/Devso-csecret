# MetaKGP Bot Frontend - Visual Setup Guide

## 🎬 Step-by-Step Visual Guide

### STEP 1: Check You Have Everything
```
Your Current Folder:
devsoc 2/
├── ✅ bot.py              (your bot)
├── ✅ faiss_index/        (vector DB)
├── ✅ metakgp_graph.gml   (knowledge graph)
└── ✅ metakgp_data/       (training data)

After Integration:
devsoc 2/
├── ✅ bot.py              (unchanged)
├── ✅ app.py              (NEW - backend)
├── ✅ static/
│   ├── index.html        (NEW - UI)
│   ├── styles.css        (NEW - styling)
│   └── script.js         (NEW - logic)
├── ✅ run.py             (NEW - launcher)
├── ✅ requirements.txt    (UPDATED)
└── ✅ [docs]             (NEW - 5 files)
```

---

## 🔧 STEP 2: Install Dependencies

### On Windows:
```powershell
# Open PowerShell or Command Prompt
# Navigate to your project folder
cd C:\Users\Admin\Desktop\DEVSOCSECRET\Devso-csecret\devsoc 2

# Install requirements
pip install -r requirements.txt

# Wait for completion (should see "Successfully installed ...")
```

### On Mac/Linux:
```bash
cd ~/path/to/devsoc\ 2
pip3 install -r requirements.txt
```

---

## 🚀 STEP 3: Run the Bot

### Option A: Windows - Easiest Way
```
Double-click: run.bat
```

### Option B: Any Platform - Recommended
```bash
python run.py
```

### Option C: Manual
```bash
python app.py
```

---

## 📊 STEP 4: Expected Console Output

When you run the bot, you should see:

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

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### ✅ What This Means:
- ✓ Vector DB loaded successfully
- ✓ Knowledge Graph loaded successfully
- ✓ Server is running on http://127.0.0.1:5000
- ✓ Ready to open in browser

### ❌ If You See Errors:
```
Error: ModuleNotFoundError: No module named 'flask'
→ Run: pip install -r requirements.txt

Error: FAISS index not found
→ Run: python ingest_modal.py

Error: Port 5000 already in use
→ Change port in app.py or kill the process
```

---

## 🌐 STEP 5: Open Frontend in Browser

### After Server Starts:
1. Open your browser
2. Go to: **http://127.0.0.1:5000**

You should see:

```
┌─────────────────────────────────────────────────┐
│           MetaKGP RAG Bot                       │
│  ┌─────────────────────────────────────────┐   │
│  │ Welcome to MetaKGP Bot! 👋               │   │
│  │                                          │   │
│  │ Ask me anything about:                  │   │
│  │ ✓ Club information (TFPS, TLS, etc.)  │   │
│  │ ✓ Hall details (RP, RK, etc.)         │   │
│  │ ✓ Officer information                 │   │
│  │                                        │   │
│  │ ┌────────────────────────────────┐    │   │
│  │ │ Ask about IIT Kharagpur...     │ ➤  │   │
│  │ └────────────────────────────────┘    │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Status: ● Online       ⚙️ Settings            │
└─────────────────────────────────────────────────┘
```

---

## 💬 STEP 6: Start Chatting!

### Example 1:
```
You: Who is the VP of TFPS?

Bot: The Vice President of Technology Film and 
     Photography Society is [name] as per the 
     MetaKGP database.
     ✓ Verified by MoE Experts
     10:30 AM
```

### Example 2:
```
You: Tell me about Rajendra Prasad Hall

Bot: Rajendra Prasad (RP) Hall of Residence is one 
     of the halls at IIT Kharagpur. It houses [X] 
     students and is known for...
     ✓ Verified by MoE Experts
     10:32 AM
```

### Example 3:
```
You: What clubs are there?

Bot: IIT Kharagpur has several clubs including:
     - Technology Film and Photography Society (TFPS)
     - Technology Literary Society (TLS)
     - Technology Students' Gymkhana (TSG)
     [more clubs...]
     ✓ Verified by MoE Experts
     10:35 AM
```

---

## 🎮 Features to Try

### 1. Sidebar Menu
```
+ New Chat        → Start fresh conversation
📋 History        → See past messages
⚙️  Settings       → Change theme, check status
● Online          → Shows if bot is running
```

### 2. Chat Features
```
Type message      → Type your question
Press Enter       → Send message
Shift+Enter       → New line in message
See timestamp     → Shows when message was sent
Verification ✓    → Shows MoE verification status
```

### 3. History Modal
```
Click 📋 History  → Opens conversation history
Click message     → Re-use past question
Clear All         → Remove all history
```

### 4. Settings Modal
```
Click ⚙️ Settings  → Opens settings
API Status        → Shows ✓ Online or ✗ Offline
Theme             → Choose Light/Dark/Auto
Response Level    → Normal or Detailed
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `Ctrl+A` | Select all (in input) |
| `Ctrl+C` | Stop server (in terminal) |

---

## 🧪 Testing Checklist

- [ ] Server starts without errors
- [ ] "Vector DB: ✓ Loaded" shown
- [ ] "Graph: ✓ Loaded" shown
- [ ] Browser opens to http://127.0.0.1:5000
- [ ] Chat interface displays
- [ ] Status dot is green (Online)
- [ ] Can type a message
- [ ] Can send message (Enter key)
- [ ] Bot responds
- [ ] Response has ✓ Verified badge
- [ ] Message appears in history
- [ ] History modal shows messages
- [ ] Settings modal opens
- [ ] Theme can be changed
- [ ] All features work

---

## 📊 What's Happening Behind the Scenes

```
Browser                    Server
  ║                          ║
  ║ 1. Type message          ║
  ╠─────────────────────────▶║ app.py receives
  ║                          ║
  ║                          ║ 2. Processes
  ║                          ║ bot.py called
  ║                          ║ ├─ Planning
  ║                          ║ ├─ Execution
  ║ 3. Typing indicator      ║ ├─ MoE Verification
  ║ shows (...)              ║ └─ Synthesis
  ║                          ║
  ║ 4. Response received     ║ 3. Response ready
  ║◀─────────────────────────╠
  ║                          ║
  ║ 5. Display in chat       ║ (done)
  ║ Add to history           ║
  ║ Show verification badge  ║
  ║                          ║
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'flask'"
```
❌ Problem: Dependencies not installed
✅ Solution:
   pip install -r requirements.txt
```

### Issue 2: "FAISS index not found"
```
❌ Problem: Vector database missing
✅ Solution:
   python ingest_modal.py
```

### Issue 3: "Port 5000 already in use"
```
❌ Problem: Another app using the port
✅ Solution A: Change port in app.py (line ~380)
   app.run(debug=True, host='127.0.0.1', port=8080)

✅ Solution B: Kill the process
   # Windows:
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
```

### Issue 4: "Bot is offline" (red dot)
```
❌ Problem: Server crashed or not running
✅ Solution:
   • Check terminal for errors
   • Restart: python run.py
   • Check console for error messages
```

### Issue 5: "Slow responses (15+ seconds)"
```
❌ Problem: Not really a problem!
ℹ️ Expected behavior:
   • Planning: 2 sec
   • Execution: 3 sec
   • MoE Verification: 5 sec (3 experts!)
   • Synthesis: 2 sec
   Total: ~12 seconds is normal
```

---

## 🔗 Important URLs

```
Application:    http://127.0.0.1:5000
API Status:     http://127.0.0.1:5000/api/status
API History:    http://127.0.0.1:5000/api/history
```

---

## 📚 Documentation Files

- **QUICK_REFERENCE.md** - Fast lookup (start here!)
- **FRONTEND_SETUP.md** - Complete setup guide
- **ARCHITECTURE.md** - System design
- **INTEGRATION_SUMMARY.md** - What changed
- **CHANGES_SUMMARY.txt** - File changes

---

## 🎯 Summary

```
1. pip install -r requirements.txt        (setup)
2. python run.py                          (start)
3. http://127.0.0.1:5000                  (open)
4. Type a question                        (chat)
5. Watch bot respond                      (verify)
```

Done! Your bot is ready to use! 🎉

---

## 💡 Pro Tips

1. **Multiple Windows**
   - Keep 1 terminal for server
   - Use 1+ browser windows for chat
   - Open DevTools (F12) for debugging

2. **Testing Queries**
   - "Who is the VP of TFPS?" (test acronym expansion)
   - "Tell me about RP Hall" (test entity recognition)
   - "Current officers" (test temporal filtering)

3. **Monitoring**
   - Watch server terminal for logs
   - Check /api/status for health
   - Use browser DevTools for API calls

4. **Development**
   - Edit static/script.js to modify UI
   - Edit static/styles.css to change styling
   - Edit app.py to add API endpoints
   - bot.py is unchanged (keep it that way!)

---

**Everything is ready. Start with `python run.py` and enjoy! 🚀**
