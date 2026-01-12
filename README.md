
# MCP + Ollama 미니 프로젝트

이 레포지토리는 LLM, MCP, 웹 크롤링을 학습하기 위한 최소한의 스캐폴드입니다. 주요 기능은 다음과 같습니다.

- 블로그(URL) 입력 받기
- 블로그 본문을 크롤링(요청 + BeautifulSoup)하여 텍스트 추출
- 로컬 Ollama LLM으로 본문 요약 및 핵심 포인트(3~5개) 추출
- O/X 형식의 퀴즈 5개 자동 생성
- 결과를 마크다운 파일로 생성하여 MCP 파일시스템 서버에 저장

Docker Compose로 로컬에서 실행할 수 있도록 구성되어 있습니다 (`docker-compose.yml`).

프로젝트 구조 (요약):

- `app/` — 콘텐츠 추출, Ollama 호출, 요약 및 퀴즈 생성 담당 Python 서비스
- `mcp_server/` — 마크다운 파일을 저장/조회하는 간단한 MCP 파일시스템 HTTP 서버
- `docker-compose.yml` — `app`과 `mcp` 서비스를 함께 띄우기 위한 설정

주요 파일 설명:

- `docker-compose.yml`: `app`(포트 8000)과 `mcp`(포트 3000)를 정의합니다. `app`은 `OLLAMA_HOST`와 `MCP_HOST` 환경변수를 사용합니다.
- `app/main.py`: Flask 기반의 엔트리 포인트—`/process` 엔드포인트로 URL을 받아 처리 로직 연결 예정입니다.
- `app/requirements.txt`: `flask`, `requests`, `beautifulsoup4`, `python-dotenv` 등 필요한 패키지 목록입니다.
- `mcp_server/server.py`: `POST /upload`으로 `{ filename, content }`를 받아 디스크에 저장하고, `GET /files` 등으로 조회할 수 있습니다.

간단 실행 방법 (루트에서):

```bash
docker-compose up --build
```

환경 변수 예시는 `.env.example`을 참고하세요. 로컬 Ollama가 `host.docker.internal:11434`에 바인딩되어 있으면, `OLLAMA_HOST`를 해당 값으로 설정하면 됩니다.

다음 권장 작업:

1. `app`에 블로그 크롤링(본문 추출) 로직 구현
2. Ollama API 호출으로 요약 및 핵심문장 추출 구현
3. 퀴즈 생성 로직 작성 후 `mcp`에 마크다운 업로드 연결

원하시면 다음 단계로 블로그 추출 기능부터 바로 구현해 드리겠습니다.
