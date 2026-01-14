# Frontend Setup & Testing Guide

## ✅ Completed Components

### React Frontend (localhost:5173)
- ✅ App.jsx: Full React component with API integration
- ✅ App.css: Modern, responsive styling
- ✅ Vite dev server: Running and auto-reloading
- ✅ Three action buttons: Extract, Process (Summary), Quiz
- ✅ Tab-based result display (본문, 요약, 퀴즈)
- ✅ Quiz card rendering with importance/difficulty badges

### Flask Backend (localhost:8000)
- ✅ CORS enabled (flask-cors installed)
- ✅ /extract endpoint: Extract text from URL
- ✅ /process endpoint: Extract + summarize
- ✅ /quiz endpoint: Extract + generate quiz
- ✅ has_cjk() function: Filter Chinese/Japanese characters
- ✅ text_length field: Added to all responses

## 🚀 Running the Application

### Prerequisites
- Python 3.11+ with venv activated
- Node.js v25.2.1 with npm 11.6.2
- Ollama running on localhost:11434 (for summarization & quiz features)

### Terminal 1: Start Flask Backend
```bash
cd app
python main.py
```
Expected output:
```
Starting server on port 8000
Ollama host: http://localhost:11434, Model: llama2
 * Running on http://0.0.0.0:8000
```

### Terminal 2: Start Vite Frontend
```bash
cd frontend
npm run dev
```
Expected output:
```
  VITE v7.2.5  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### Terminal 3: Start Ollama (if not already running)
```bash
ollama serve
```

## 🧪 Testing the Application

### Test 1: Extract Text from URL
1. Open http://localhost:5173
2. Enter URL: `https://www.wikipedia.org/wiki/Artificial_intelligence`
3. Click "추출" button
4. Verify: Text extracted and displayed in "본문" tab

### Test 2: Summarize Content
1. Use same URL from Test 1
2. Click "요약" button
3. Verify: Summary displayed in "요약" tab (2-3 Korean sentences)

### Test 3: Generate Quiz
1. Use same URL from Test 1
2. Click "퀴즈" button
3. Verify: 4-5 O/X quizzes displayed in "퀴즈" tab with:
   - Question text (no Chinese/Japanese characters)
   - Answer (O or X)
   - Importance badge (높음, 중간, 낮음)
   - Difficulty score (1-3)
   - Explanation

### Test 4: Error Handling
1. Try empty URL input → Should show error message
2. Try invalid URL → Should show API error
3. Try very long URL with special characters → Should handle gracefully

## 🎨 UI Features

### Input Section
- URL input field with placeholder
- Enter key support (auto-submit on Enter)
- Three action buttons (disabled during loading)
- Loading indicator ("처리중..." text)

### Result Section
- Title and character count display
- Conditional tab rendering (only show tabs with data)
- Tab switching animation
- Quiz cards with:
  - Question number (Q1, Q2, etc.)
  - Importance badge styling
  - Difficulty indicator
  - Answer display (O/X)
  - Explanation text

### Error Handling
- User-friendly error messages
- Clear error messages from API
- Form validation (URL required)

## 🔗 API Endpoints Reference

### POST /extract
```json
Request:  { "url": "https://example.com" }
Response: {
  "url": "https://example.com",
  "title": "Page Title",
  "text": "Full extracted text...",
  "text_length": 2341
}
```

### POST /process
```json
Request:  { "url": "https://example.com" }
Response: {
  "url": "https://example.com",
  "title": "Page Title",
  "text_length": 2341,
  "summary": "Korean summary (2-3 sentences)..."
}
```

### POST /quiz
```json
Request:  { "url": "https://example.com" }
Response: {
  "url": "https://example.com",
  "title": "Page Title",
  "quiz_count": 5,
  "quiz": [
    {
      "question": "질문 내용",
      "answer": true,
      "difficulty": 2,
      "importance": "높음",
      "explanation": "설명 텍스트"
    },
    ...
  ]
}
```

## 📦 Dependencies Installed

### Backend (Python)
- flask-cors: CORS support for cross-origin requests
- flask: Web framework
- requests: HTTP client for Ollama API
- beautifulsoup4: HTML parsing

### Frontend (Node.js)
- react: UI library
- react-dom: React DOM rendering
- vite: Build tool & dev server

## 🐛 Troubleshooting

### CORS Errors
- Ensure `CORS(app)` is called in Flask app
- Check that flask-cors is installed: `pip install flask-cors`

### Ollama Connection Errors
- Verify Ollama is running: `ollama serve`
- Check Ollama port 11434 is accessible
- Model available: `ollama pull llama2`

### Frontend Not Loading
- Check Vite dev server is running (localhost:5173)
- Clear browser cache
- Check console for JavaScript errors

### No Quiz Generated
- Verify text extraction succeeded (check "본문" tab)
- Check Ollama server is responsive
- Try shorter URLs with simpler content
- Check Flask server logs for errors

## 📝 Next Steps

### Stage 2 (Planned)
- [ ] MCP (Model Context Protocol) server integration
- [ ] Database storage (PostgreSQL)
- [ ] User authentication
- [ ] Quiz history & statistics
- [ ] Keyboard shortcuts
- [ ] Loading animations
- [ ] Dark mode toggle

### Optimization
- [ ] Cache extracted content
- [ ] Improve Ollama response time
- [ ] Add progress bar for long requests
- [ ] Implement request cancellation

## 🔄 Code Architecture

### Frontend Flow
```
User Input (URL)
    ↓
handleProcess(endpoint)
    ↓
fetch() to Flask API
    ↓
Update State (result, activeTab)
    ↓
Render Result (tabs + content)
```

### Backend Flow
```
POST /quiz (URL)
    ↓
fetch_html(url)
    ↓
extract_text(html)
    ↓
generate_quiz_with_ollama(text)
    ↓
Return JSON {url, title, quiz_count, quiz}
```

---

**Last Updated:** 2024-01-14  
**Frontend Status:** ✅ Ready for testing  
**Backend Status:** ✅ Ready with CORS  
**Overall:** Ready for full integration testing
