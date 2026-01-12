from app.extract import extract_text


def test_extract_from_simple_html():
    html = """
    <html>
      <head><title>테스트 문서</title></head>
      <body>
        <div id="post-content">
          <h1>문서 제목</h1>
          <p>첫 문단입니다.</p>
          <p>두 번째 문단입니다.</p>
        </div>
      </body>
    </html>
    """
    title, text = extract_text(html)
    assert '테스트 문서' in title or '문서 제목' in title
    assert '첫 문단' in text
    assert '두 번째 문단' in text


def test_extract_fallback_paragraphs():
    html = """
    <html>
      <head><title></title></head>
      <body>
        <p>하나.</p>
        <p>둘.</p>
        <p>셋.</p>
      </body>
    </html>
    """
    title, text = extract_text(html)
    assert text.count('\n\n') >= 1
    assert '하나.' in text
