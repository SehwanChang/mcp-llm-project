# MCP + Ollama 미니 프로젝트

이 프로젝트는 LLM, MCP, 웹 크롤링을 학습하기 위한 스캐폴드입니다. URL에서 웹페이지 본문을 추출하고, Ollama를 사용해 요약 및 퀴즈를 자동 생성합니다.

## 주요 기능

- ✅ **HTML 본문 추출** — `requests` + `BeautifulSoup`로 웹페이지에서 제목과 본문 텍스트 자동 추출
- 🔄 **Ollama LLM 연동** — 추출된 텍스트를 요약하고 핵심 포인트 추출 (구현 예정)
- 📝 **자동 퀴즈 생성** — O/X 형식 퀴즈 5개 자동 생성 (구현 예정)
- 💾 **MCP 파일서버 연동** — 마크다운 결과를 MCP 파일시스템에 저장 (구현 예정)
- 🐳 **Docker Compose** — 로컬에서 모든 서비스 자동 실행

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

### 2. HTML 본문 추출 (URL 사용)

```bash
cd app
python extract.py 'https://example.com'
```

**출력:**
```
Fetching: https://example.com

=== TITLE ===
Example Domain

=== EXTRACT (first 1000 chars) ===
This domain is for use in examples...

[chars] 1234
```

### 3. 샘플 HTML로 추출 결과 확인

```bash
# 로컬 HTML 샘플로 테스트 (파일 저장 없음)
python scripts/dump_extract_samples.py
```

**출력:**
```
--- simple_html ---
TITLE: 테스트 문서
TEXT:
 문서 제목
첫 문단입니다.
두 번째 문단입니다.

--- fallback_paragraphs ---
TITLE: 
TEXT:
 하나.

둘.

셋.

Wrote detailed results to: .extract_samples.json
```

### 4. Docker Compose로 전체 서비스 실행

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
| 1 | `extract.py` 옵션 확장 | `--file`, `--html` 옵션으로 파일/문자열 입력 지원 |
| 2 | 테스트 확장 | 한글 인코딩, 빈 본문, 스크립트 제거 등 엣지 케이스 추가 |
| 3 | Ollama 연동 | `main.py`에서 Ollama API 호출로 요약 및 핵심 추출 |
| 4 | 퀴즈 생성 | LLM으로 O/X 형식 퀴즈 5개 자동 생성 |
| 5 | MCP 연동 | 결과를 마크다운으로 생성해 MCP 파일서버에 저장 |

## 기여하기

[CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요. 주요 컨벤션:
- 커밋 형식: `유형(범위): 설명` (예: `수정(extract): 인코딩 개선`)
- 테스트: PR 전에 `pytest -q` 실행
- 브랜치: 기능별 브랜치 생성 후 PR

## 라이선스

MIT (또는 프로젝트에 맞는 라이선스)
