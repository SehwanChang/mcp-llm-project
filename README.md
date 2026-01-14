# MCP + Ollama 미니 프로젝트

이 프로젝트는 LLM, MCP, 웹 크롤링을 학습하기 위한 스캐폴드입니다. URL에서 웹페이지 본문을 추출하고, Ollama를 사용해 요약 및 퀴즈를 자동 생성합니다.

## 주요 기능

- ✅ **HTML 본문 추출** — `requests` + `BeautifulSoup`로 웹페이지에서 제목과 본문 텍스트 자동 추출
  - 옵션: URL, 로컬 파일, HTML 문자열 입력 지원
  - 출력: 일반 텍스트 또는 JSON 포맷
- ✅ **Ollama LLM 연동** — 추출된 텍스트를 한글로 자동 요약 (2-3문장)
  - Flask API 엔드포인트: `/process` (URL 입력 → 추출 + 요약)
- 📝 **자동 퀴즈 생성** — O/X 형식 퀴즈 5개 자동 생성 (구현 예정)
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

| 우선순위 | 작업 | 설명 |
|---------|------|------|
| 1 | **퀴즈 생성** | Ollama로 O/X 형식 퀴즈 5개 자동 생성 |
| 2 | **MCP 연동** | 결과를 마크다운으로 저장해 MCP 파일서버에 업로드 |
| 3 | **API 응답 개선** | 에러 처리 강화, 타임아웃 처리 추가 |
| 4 | **테스트 확장** | 한글 인코딩, 빈 본문, 스크립트 제거 등 엣지 케이스 |
| 5 | **다른 모델 지원** | llama2 외 다른 Ollama 모델 사용 가능하도록 확장 |

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
