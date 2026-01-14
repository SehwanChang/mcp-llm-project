from flask import Flask, request, jsonify
import os
import requests
import json
from extract import fetch_html, extract_text

app = Flask(__name__)

# Ollama API 설정
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')


def summarize_with_ollama(text, max_tokens=100):
    """Ollama를 사용하여 텍스트를 요약합니다."""
    try:
        prompt = f"""다음 텍스트를 한국어로 2-3 문장으로 간결하게 요약하세요. 최대 100자 이내:

{text[:500]}

요약:"""
        
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:
        return f'(요약 실패: {str(e)})'


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/process', methods=['POST'])
def process():
    """URL의 본문을 추출하고 Ollama로 요약합니다."""
    try:
        data = request.json or {}
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'url required'}), 400
        
        # 1. HTML 가져오기
        print(f'Fetching: {url}')
        html = fetch_html(url)
        
        # 2. 본문 추출
        title, text = extract_text(html, url=url)
        
        # 3. Ollama로 요약
        print('Summarizing with Ollama...')
        summary = summarize_with_ollama(text)
        
        return jsonify({
            'url': url,
            'title': title,
            'text_length': len(text),
            'summary': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/extract', methods=['POST'])
def extract_only():
    """URL의 본문만 추출 (요약 없음)"""
    try:
        data = request.json or {}
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'url required'}), 400
        
        html = fetch_html(url)
        title, text = extract_text(html, url=url)
        
        return jsonify({
            'url': url,
            'title': title,
            'text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'Starting server on port {port}')
    print(f'Ollama host: {OLLAMA_HOST}, Model: {OLLAMA_MODEL}')
    app.run(host='0.0.0.0', port=port, debug=False)
