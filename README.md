# MCP + Ollama 미니 프로젝트

이 프로젝트는 LLM, MCP, 웹 크롤링을 학습하기 위한 스캐폴드입니다. URL에서 웹페이지 본문을 추출하고, Ollama를 사용해 요약 및 퀴즈를 자동 생성합니다.

> 📖 **[💻 사용 설명서](./USAGE.md)** ← 프로그램 사용하는 방법은 여기서 확인하세요!

## 주요 기능

- ✅ **HTML 본문 추출** — `requests` + `BeautifulSoup`로 웹페이지에서 제목과 본문 텍스트 자동 추출
  - 옵션: URL, 로컬 파일, HTML 문자열 입력 지원
  - 출력: 일반 텍스트 또는 JSON 포맷
- ✅ **Ollama LLM 연동** — 추출된 텍스트를 한글로 자동 요약 (2-3문장)
  - Flask API 엔드포인트: `/process` (URL 입력 → 추출 + 요약)
- ✅ **자동 퀴즈 생성** — O/X 형식 퀴즈 5개 자동 생성 (완성)
  - 단호한 서술문 형식 (의문형 금지)
  - 순수 한글 필터링 (한자, 외래어 제거)
  - 중요도/난이도 자동 할당
- 💾 **MCP 파일서버 연동** — 마크다운 결과를 MCP 파일시스템에 저장 (구현 예정)
- 🐳 **Docker Compose** — 로컬에서 모든 서비스 자동 실행
- 🔄 **GitHub Actions CI** — 푸시/PR 시 자동 테스트

## 프로젝트 구조

```
.
├── app/                          # 콘텐츠 추출 & 처리 서비스
│   ├── extract.py               # HTML 본문 추출 로직 (완성)
│   ├── main.py                  # Flask 서버 엔트리포인트
│   ├── requirements.txt
│   └── Dockerfile
├── mcp_server/                   # MCP 파일시스템 HTTP 서버
│   ├── server.py
│   ├── requirements.txt
│   └── Dockerfile
├── tests/                        # 단위 테스트
│   └── test_extract.py          # extract.py 테스트 (2개 케이스, 통과)
├── scripts/                      # 유틸리티 스크립트
│   ├── run_tests.py             # pytest 실행 및 결과 저장
│   └── dump_extract_samples.py  # 샘플 HTML로 추출 결과 확인
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions CI (자동 테스트)
├── docker-compose.yml           # Docker 서비스 정의
├── CONTRIBUTING.md              # 커밋 및 PR 컨벤션
└── README.md                    # 이 파일
```

## 빠른 시작

### 1. 로컬 테스트 실행

```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r app/requirements.txt
pip install pytest

# 단위 테스트 실행
pytest -q tests/test_extract.py
```

**결과:**
```
.. [100%] 
2 passed
```

### 2. HTML 본문 추출 (다양한 옵션)

**URL에서 추출:**
```bash
cd app
python extract.py 'https://example.com'
```

**로컬 파일에서 추출:**
```bash
cd app
python extract.py --file /path/to/file.html
```

**HTML 문자열로 추출:**
```bash
cd app
python extract.py --html '<html><body><p>Hello</p></body></html>'
```

**JSON 형식 출력:**
```bash
cd app
python extract.py --file sample.html --json
```

**출력 예시:**
```json
{
  "title": "Example Domain",
  "text": "This domain is for use in examples...",
  "char_count": 1234
}
```

### 3. Ollama로 자동 요약

먼저 Ollama가 설치되고 실행 중이어야 합니다.

**Ollama 설치 및 모델 다운로드:**
```bash
# 설치 (macOS)
# 1) ollama.ai에서 다운로드 후 설치
# 2) 또는: brew install ollama

# 모델 다운로드 (처음 1회, ~3.8GB)
ollama pull llama2

# 서버 실행 (백그라운드)
ollama serve &
```

**요약 테스트:**
```bash
# 로컬 HTML로 요약 테스트
python scripts/test_ollama_integration.py
```

**출력 예시:**
```
==================================================
[1단계] HTML에서 본문 추출
==================================================
제목: 인공지능의 미래
본문 (처음 200자):
인공지능(AI)은 최근 몇 년간 놀라운 발전을 이루었습니다...

==================================================
[2단계] Ollama로 요약
==================================================
[요청] Ollama (llama2)로 요약 중...
요약:
인공지능(AI)은 최근 몇 년간 놀라운 발전을 이루었습니다. AI는 자연어 처리 기술과 함께 의료, 금융, 교육 등 다양한 분야에서 혁신을 일으키고 있습니다. 하지만, AI의 올바른 활용과 규제의 균형이 중요하다고 전문가들은 강조합니다.

결과 저장됨: .ollama_test.json
```

Flask API 서버를 시작하면 추출 + 요약을 한 번에 처리할 수 있습니다.

```bash
# 루트 디렉토리에서 환경변수 설정
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama2

# Flask 서버 시작
cd app
python main.py
```

**API 엔드포인트 사용:**

1. **건강 체크:**
```bash
curl http://localhost:8000/health
```

2. **URL 추출 + 요약 (전체 파이프라인):**
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**응답 예시:**
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "text_length": 1234,
  "summary": "Example 도메인은 예시용으로 사용됩니다. 이 도메인은 인터넷 표준 문서에서 예제로 사용되도록 예약되어 있습니다."
}
```

3. **URL 추출만 (요약 없음):**
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

4. **O/X 퀴즈 생성:**
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**응답 예시:**
```json
{
  "url": "https://example.com",
  "title": "인공지능의 미래",
  "quiz_count": 4,
  "quiz": [
    {
      "question": "인공지능은 세상을 바꾸고 있다.",
      "answer": true,
      "difficulty": 3,
      "importance": "높음",
      "explanation": "본문의 내용을 근거로 합니다."
    },
    {
      "question": "AI는 의료에서 발전하고 있지 않다.",
      "answer": false,
      "difficulty": 2,
      "importance": "중간",
      "explanation": "본문의 내용을 근거로 합니다."
    }
  ]
}
```

### 5. Docker Compose로 전체 서비스 실행

```bash
# 루트에서 실행
docker-compose up --build
```

- `app` 서비스: 포트 8000 (Flask API)
- `mcp_server` 서비스: 포트 3000 (파일시스템 HTTP 서버)

환경변수 설정은 `.env.example`을 참고하세요.

## 주요 파일 설명

### `app/extract.py`
웹페이지 HTML에서 제목과 본문 텍스트를 추출하는 핵심 모듈입니다.

**함수:**
- `fetch_html(url, timeout=10)` — URL에서 HTML 콘텐츠 가져오기
- `extract_text(html, url=None)` — HTML에서 제목과 본문 추출 (title, text) 튜플 반환

**추출 전략:**
1. `<article>`, `<main>` 태그 검색
2. id/class가 'content', 'article', 'post', 'entry', 'main' 포함하는 요소 검색
3. 위가 없으면 모든 `<p>` 태그를 수집하여 가장 긴 연속 블록 추출
4. 마지막 수단: body 전체 텍스트

**사용 예:**
```python
from app.extract import extract_text, fetch_html

# URL에서 추출
html = fetch_html('https://example.com')
title, text = extract_text(html)
print(f"제목: {title}")
print(f"본문: {text[:100]}...")

# 로컬 HTML 문자열에서 추출
html_string = '<html><body><p>Hello</p></body></html>'
title, text = extract_text(html_string)
```

### `tests/test_extract.py`
`extract_text` 함수의 단위 테스트입니다. 로컬 HTML 샘플로 추출 로직을 검증합니다.

**테스트 케이스:**
- `test_extract_from_simple_html` — id 기반 선택자로 본문 추출
- `test_extract_fallback_paragraphs` — 모든 `<p>` 태그 폴백 추출

### `scripts/test_ollama_integration.py`
Ollama 연동을 테스트하는 스크립트입니다. 로컬 HTML을 추출한 후 Ollama로 요약하는 파이프라인을 검증합니다.

**동작:**
1. 테스트용 HTML 본문 추출
2. Ollama API 호출해 한글 요약
3. 결과를 `.ollama_test.json`으로 저장

**실행:**
```bash
python scripts/test_ollama_integration.py
```

### `app/main.py`
Flask 기반 HTTP API 서버입니다. 웹페이지 본문 추출 후 Ollama로 자동 요약합니다.

**함수:**
- `summarize_with_ollama(text)` — Ollama API 호출해 한글 2-3문장 요약
- `POST /health` — 서버 상태 확인
- `POST /process` — URL 입력 → 추출 + 요약 (전체 파이프라인)
- `POST /extract` — URL 입력 → 추출만 (요약 없음)

**환경변수:**
- `OLLAMA_HOST` — Ollama 서버 주소 (기본값: `http://localhost:11434`)
- `OLLAMA_MODEL` — 사용할 모델명 (기본값: `llama2`)
- `PORT` — Flask 포트 (기본값: `8000`)

### `.github/workflows/ci.yml`
GitHub Actions 자동 테스트 파이프라인입니다.

**동작:**
- 주기: `main` 브랜치 푸시 또는 PR 생성 시
- 환경: Ubuntu Latest, Python 3.11
- 단계:
  1. 코드 체크아웃
  2. Python 3.11 설치
  3. 의존성 설치 (pip 캐시)
  4. `pytest -q` 실행
- 결과: GitHub UI에서 ✅/❌ 표시

## 다음 단계

| 우선순위 | 작업 | 상태 | 설명 |
|---------|------|------|------|
| 1 | **퀴즈 생성** | ✅ 완성 | O/X 형식 5개, 한자 필터링, 중요도/난이도 자동 할당 |
| 2 | **API 테스트** | 📝 진행중 | Flask `/quiz` 엔드포인트 로컬 테스트 |
| 3 | **MCP 연동** | ⬜ 예정 | 결과를 마크다운으로 저장해 MCP 파일서버에 업로드 |
| 4 | **Stage 2 개선** | ⬜ 예정 | 더 정확한 키워드 추출, 핵심 개념 감지, JSON 응답 개선 |
| 5 | **테스트 확장** | ⬜ 예정 | 한글 인코딩, 빈 본문, 스크립트 제거 등 엣지 케이스 |

**Stage 1 완성 항목:**
- ✅ HTML 추출 (URL, 파일, HTML 문자열)
- ✅ Ollama 요약 (한글 2-3문장)
- ✅ O/X 퀴즈 생성 (4-5개)
  - 단호한 서술문만 (의문형 제거)
  - 순수 한글만 (한자/외래어 필터링)
  - 중요도/난이도 자동 할당
- ✅ Flask API (`/health`, `/extract`, `/process`, `/quiz`)
- ✅ GitHub Actions CI
- ✅ 단위 테스트

---

## 📋 개선사항 (사용자 피드백 기반)

### 🔴 고우선순위 (Core UX 개선)

#### 1. **퀴즈 정답 숨기기** (필수)
- **문제:** 현재 정답을 바로 표시함 (사용자가 먼저 풀 수 없음)
- **해결:** 정답 버튼 추가 → 클릭 시 정답 공개
- **영향:** 퀴즈 기능의 핵심 개선
- **예상 난이도:** 중간 (React 상태 관리)

#### 2. **추출 기능 제거 및 UI 단순화**
- **문제:** 추출 기능이 불필요하고 혼동 유발
- **해결:** `/extract` 엔드포인트 제거, 프론트 [추출] 버튼 삭제
- **변경 후:** 요약 → 퀴즈 2개만 표시
- **영향:** UI 간결화, 사용자 혼동 제거
- **예상 난이도:** 낮음 (간단한 제거 작업)

#### 3. **정답 중복 표시 제거**
- **문제:** "정답: ⭕ O" 형식으로 2중 표시
- **해결:** "정답 공개 버튼" 구현 시 "O" 또는 "X" 중 하나만 표시
- **영향:** UX 개선
- **예상 난이도:** 낮음

#### 4. **"높음/중간/낮음" 라벨 명확화**
- **문제:** 사용자가 의미를 모름 ("높음"이 뭔가?)
- **해결:** 라벨에 설명 추가 (마우스 호버 시 "중요도: 본문에서 다루는 정도" 표시)
- **대안:** 배지에 "중요도" 라벨 텍스트 추가
- **예상 난이도:** 낮음

### 🟡 중우선순위 (품질 개선)

#### 5. **해설(Explanation) 품질 개선**
- **문제:** "본문의 내용을 근거로 합니다" 같은 빈약한 해설
- **해결:** AI 프롬프트 개선
  - 구체적인 본문 구절 인용
  - "왜 이 답이 맞는가" 설명
  - 예: "문장 '~는 ~이다'에서 알 수 있듯이..."
- **영향:** 학습 효과 증대
- **예상 난이도:** 높음 (Ollama 프롬프트 엔지니어링)

#### 6. **PC 화면 최적화**
- **문제:** UI가 모바일 중심으로 설계됨
- **해결:** 
  - 데스크톱 (1200px+): 2단 레이아웃 (입력 + 결과 나란히)
  - 퀴즈 카드: 더 큰 글씨, 여유로운 패딩
  - 버튼 크기 조정
- **예상 난이도:** 중간 (CSS 미디어쿼리 추가)

#### 7. **설명 텍스트 수정**
- **문제:** "웹 기사" → 일반 콘텐츠로 변경 필요
- **해결:** 
  - 제목: "웹 기사 → 자동 요약 & 퀴즈" → "콘텐츠 → 자동 요약 & 퀴즈"
  - 안내 텍스트: "웹사이트", "웹페이지" → "콘텐츠", "URL"
- **예상 난이도:** 낮음

### 🟢 저우선순위 (기술 검토)

#### 8. **Rolldown-Vite 기술 스택 검토**
- **문제:** 새로운 번들러(Rolldown) 사용 중인데, 장기 지원 불확실
- **검토:** 
  - 표준 Vite로 마이그레이션 필요할 수 있음
  - 향후 호환성 문제 모니터링
- **예상 난이도:** 높음 (번들러 전환)
- **타이밍:** 안정화 후 Stage 2

---

## 개발 로드맵

### Phase 1: 필수 UX 개선 (이번 스프린트)
```
1순위: 퀴즈 정답 숨기기 & 공개 버튼 → [정답 보기]
2순위: 추출 기능 제거 (간단함)
3순위: PC UI 최적화
4순위: 라벨 명확화 ("중요도", "관련도" 추가)
```

### Phase 2: 품질 개선 (다음 스프린트)
```
- AI 해설 프롬프트 개선
- 설명 텍스트 일관성 수정
- 모바일/PC 최종 테스트
```

### Phase 3: 고급 기능 (Stage 2)
```
- MCP 파일서버 연동
- 퀴즈 풀이 기능 (정답 저장, 점수 계산)
- 히스토리/통계
- 데이터베이스 연동
```

## 기여하기

[CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요. 주요 컨벤션:
- 커밋 형식: `유형(범위): 설명` (예: `기능(extract): 인코딩 개선`)
- 테스트: PR 전에 `pytest -q` 실행
- 브랜치: 기능별 브랜치 생성 후 PR

## 환경변수 설정

`.env.example`을 `.env`로 복사하여 설정하세요.

```bash
cp .env.example .env
```

**주요 환경변수:**
- `OLLAMA_HOST=http://localhost:11434` — Ollama 서버 주소
- `OLLAMA_MODEL=llama2` — 사용할 모델
- `PORT=8000` — Flask 포트
- `MCP_HOST=http://localhost:3000` — MCP 서버 주소 (향후)

## 라이선스

MIT (또는 프로젝트에 맞는 라이선스)
