import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

HEADERS = {
    'User-Agent': 'mcp-llm-crawler/1.0 (+https://example.com)'
}

# JavaScript 렌더링이 필요한 사이트 패턴
JS_REQUIRED_DOMAINS = [
    'velog.io',
    'tistory.com',
    'medium.com',
    'brunch.co.kr',
    'notion.site'
]


def needs_js_rendering(url):
    """URL이 JavaScript 렌더링이 필요한 사이트인지 확인"""
    return any(domain in url for domain in JS_REQUIRED_DOMAINS)


def fetch_html_with_selenium(url, timeout=15):
    """Selenium을 사용하여 JavaScript 렌더링된 HTML 가져오기"""
    options = Options()
    options.add_argument('--headless')  # 브라우저 창 안 띄움
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(timeout)
        
        driver.get(url)
        
        # JavaScript 실행 대기 (페이지 로딩)
        time.sleep(3)
        
        # article, main 또는 본문 요소가 나타날 때까지 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except:
            # article이 없어도 계속 진행
            pass
        
        html = driver.page_source
        return html
    finally:
        if driver:
            driver.quit()


def fetch_html(url, timeout=10):
    """URL에서 HTML 가져오기 (필요시 Selenium 사용)"""
    if needs_js_rendering(url):
        print(f'Using Selenium for JS rendering: {url}')
        return fetch_html_with_selenium(url, timeout)
    else:
        print(f'Using requests for static HTML: {url}')
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text


def _clean_soup(soup):
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'nav', 'aside']):
        tag.decompose()


def extract_text(html, url=None):
    """주요 본문과 타이틀을 추출하여 (title, text) 형태로 반환합니다.

    전략:
    1) <article>, <main> 우선
    2) id/class에 'content','article','post','entry','main' 포함하는 요소 검색
    3) 위가 없으면 모든 <p>를 모아 가장 긴 연속 블록 사용
    """
    soup = BeautifulSoup(html, 'html.parser')
    _clean_soup(soup)

    # title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            title = h1.get_text(strip=True)

    # 후보 선택자
    candidates = []
    article = soup.find('article')
    if article:
        candidates.append(article)
    main = soup.find('main')
    if main:
        candidates.append(main)

    # id/class 기반 검색
    pattern = re.compile(r'(content|article|post|entry|main|body)', re.I)
    for tag in soup.find_all(True):
        if tag.has_attr('id') and pattern.search(tag['id']):
            candidates.append(tag)
        elif tag.has_attr('class'):
            classes = ' '.join(tag.get('class'))
            if pattern.search(classes):
                candidates.append(tag)

    # candidate에서 텍스트 길이 기준으로 선택
    best = None
    best_len = 0
    for c in candidates:
        text = c.get_text(separator='\n', strip=True)
        if len(text) > best_len:
            best = text
            best_len = len(text)

    # fallback: 모든 <p>를 모아서 가장 긴 연속 블록 추출
    if not best:
        paragraphs = [p.get_text(' ', strip=True) for p in soup.find_all('p')]
        if paragraphs:
            # join with double newlines and choose the longest chunk
            joined = '\n\n'.join(paragraphs)
            best = joined

    if not best:
        # 마지막 수단: body 텍스트 전체
        body = soup.body
        best = body.get_text(separator='\n', strip=True) if body else ''

    # normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', best).strip()
    return title or '', text


if __name__ == '__main__':
    import sys
    import json
    import argparse
    
    parser = argparse.ArgumentParser(
        description='웹페이지 또는 HTML에서 제목과 본문을 추출합니다.',
        prog='extract.py'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='URL, 파일 경로, 또는 HTML 문자열 (기본값: 표준입력)'
    )
    parser.add_argument(
        '--file', '-f',
        action='store_true',
        help='입력을 로컬 파일 경로로 해석'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='입력을 HTML 문자열로 해석'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='결과를 JSON 형식으로 출력'
    )
    
    args = parser.parse_args()
    
    try:
        # 입력 소스 결정
        if args.file:
            # 파일에서 읽기
            if not args.input:
                print('Error: --file 옵션 사용 시 파일 경로를 지정해야 합니다.', file=sys.stderr)
                sys.exit(1)
            with open(args.input, 'r', encoding='utf-8') as f:
                html = f.read()
            print(f'파일에서 읽음: {args.input}', file=sys.stderr)
        elif args.html:
            # HTML 문자열 직접 사용
            if not args.input:
                print('Error: --html 옵션 사용 시 HTML 문자열을 지정해야 합니다.', file=sys.stderr)
                sys.exit(1)
            html = args.input
            print('HTML 문자열에서 처리', file=sys.stderr)
        elif args.input:
            # URL로 해석
            url = args.input
            print(f'URL에서 가져옴: {url}', file=sys.stderr)
            html = fetch_html(url)
        else:
            # 표준입력에서 읽기
            print('표준입력에서 읽음 (Ctrl+D로 종료)', file=sys.stderr)
            html = sys.stdin.read()
        
        # 추출 실행
        title, text = extract_text(html)
        
        # 출력
        if args.json:
            result = {
                'title': title,
                'text': text,
                'char_count': len(text)
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print('\n=== TITLE ===\n')
            print(title[:200] if title else '(제목 없음)')
            print('\n=== EXTRACT (first 1000 chars) ===\n')
            print(text[:1000])
            print('\n\n[chars]', len(text))
            
    except FileNotFoundError as e:
        print(f'Error: 파일을 찾을 수 없습니다 - {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
