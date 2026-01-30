import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('process')
  const [showGuide, setShowGuide] = useState(!result)
  const [revealedAnswers, setRevealedAnswers] = useState({})

  // 환경에 따라 API URL 자동 설정
  // 개발: localhost:8000, 배포: /api (nginx 프록시)
  const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000'

  const handleReset = () => {
    setUrl('')
    setResult(null)
    setError(null)
    setShowGuide(true)
    setRevealedAnswers({})
    setActiveTab('process')
  }

  const handleProcess = async (endpoint) => {
    if (!url.trim()) {
      setError('URL을 입력해주세요')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setShowGuide(false)
    setRevealedAnswers({})

    try {
      const response = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        throw new Error(`API 오류: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
      setActiveTab(endpoint)
    } catch (err) {
      setError(err.message || '요청 실패')
      setShowGuide(true)
    } finally {
      setLoading(false)
    }
  }

  const toggleAnswer = (idx) => {
    setRevealedAnswers(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  const renderQuizResult = () => {
    if (!result?.quiz || result.quiz.length === 0) {
      return <p className="no-data">생성된 퀴즈가 없습니다</p>
    }

    return (
      <div className="quiz-container">
        {result.quiz.map((q, idx) => (
          <div key={idx} className="quiz-card">
            <div className="quiz-header">
              <span className="quiz-num">문제 {idx + 1}</span>
              <span className="importance-badge">
                <span className="importance-label">중요도:</span>
                <span className={`importance ${q.importance}`}>{q.importance}</span>
              </span>
              <span className="difficulty">난이도: {q.difficulty}</span>
            </div>
            <div className="quiz-question">{q.question}</div>
            
            {revealedAnswers[idx] ? (
              <div className="quiz-answer revealed">
                <strong>{q.answer ? 'O' : 'X'}</strong>
              </div>
            ) : (
              <button 
                className="btn-reveal-answer"
                onClick={() => toggleAnswer(idx)}
              >
                정답 보기
              </button>
            )}
            
            <div className="quiz-explanation">{q.explanation}</div>
          </div>
        ))}
      </div>
    )
  }

  const renderGuide = () => {
    return (
      <div className="guide-section">
        <div className="guide-content">
          <h2>📖 사용 방법</h2>
          
          <div className="guide-steps">
            <div className="guide-step">
              <span className="step-badge">1️⃣</span>
              <div>
                <strong>URL 입력</strong>
                <p>https://로 시작하는 웹페이지 주소 입력</p>
              </div>
            </div>
            <div className="guide-step">
              <span className="step-badge">2️⃣</span>
              <div>
                <strong>[요약] 버튼</strong>
                <p>AI가 내용을 한국어 2-3문장으로 요약</p>
              </div>
            </div>
            <div className="guide-step">
              <span className="step-badge">3️⃣</span>
              <div>
                <strong>[퀴즈] 버튼</strong>
                <p>O/X 퀴즈 4-5개 자동 생성 (난이도/중요도 표시)</p>
              </div>
            </div>
          </div>

          <div className="guide-tips">
            <p>💡 Enter 키로 자동 실행 | 퀴즈는 여러 번 클릭해서 다양한 문제 생성 가능</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <header className="header">
        <h1 onClick={handleReset} style={{ cursor: 'pointer' }}>🎓 스마트 학습 도구</h1>
        <p>웹 기사 → 자동 요약 & 퀴즈 생성</p>
      </header>

      <section className="input-section">
        <div className="input-group">
          <input
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleProcess('process')}
            disabled={loading}
          />
          <div className="button-group">
            <button 
              onClick={() => handleProcess('process')} 
              disabled={loading}
              className="btn btn-secondary"
            >
              요약
            </button>
            <button 
              onClick={() => handleProcess('quiz')} 
              disabled={loading}
              className="btn btn-accent"
            >
              퀴즈
            </button>
          </div>
        </div>
      </section>

      {loading && (
        <div className="loading-section">
          <div className="loading-spinner"></div>
          <div className="loading-text">
            <p className="loading-main">AI가 열심히 분석 중입니다...</p>
            <p className="loading-sub">
              {activeTab === 'quiz' ? '퀴즈를 생성하고 있어요 (약 10-15초)' : '내용을 요약하고 있어요 (약 5-10초)'}
            </p>
          </div>
        </div>
      )}

      {error && <div className="error-message">⚠️ {error}</div>}

      {result ? (
        <section className="result-section">
          <div className="result-header">
            <h2>{result.title || '제목 없음'}</h2>
            <span className="text-length">본문: {result.text_length || 0}자</span>
          </div>

          <div className="tabs">
            {result.summary && (
              <button
                className={`tab ${activeTab === 'process' ? 'active' : ''}`}
                onClick={() => setActiveTab('process')}
              >
                요약
              </button>
            )}
            {result.quiz && (
              <button
                className={`tab ${activeTab === 'quiz' ? 'active' : ''}`}
                onClick={() => setActiveTab('quiz')}
              >
                퀴즈 ({result.quiz_count || result.quiz.length})
              </button>
            )}
          </div>

          <div className="tab-content">
            {activeTab === 'process' && result.summary && (
              <div className="summary-content">
                <div className="summary-box">
                  {result.summary}
                </div>
              </div>
            )}
            {activeTab === 'quiz' && renderQuizResult()}
          </div>
        </section>
      ) : (
        showGuide && renderGuide()
      )}

      <footer className="footer">
        <p>Flask API 서버: {API_BASE}</p>
      </footer>
    </div>
  )
}

export default App
