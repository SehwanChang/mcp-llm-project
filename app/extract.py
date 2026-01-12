import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'mcp-llm-crawler/1.0 (+https://example.com)'
}


def fetch_html(url, timeout=10):
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
    if len(sys.argv) < 2:
        print('Usage: python extract.py <url>')
        sys.exit(1)
    url = sys.argv[1]
    print('Fetching:', url)
    try:
        html = fetch_html(url)
        title, text = extract_text(html, url=url)
        print('\n=== TITLE ===\n')
        print(title[:200])
        print('\n=== EXTRACT (first 1000 chars) ===\n')
        print(text[:1000])
        print('\n\n[chars]', len(text))
    except Exception as e:
        print('Error:', e)
