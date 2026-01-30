from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import requests
import json
import re
from extract import fetch_html, extract_text

app = Flask(__name__)
CORS(app)

# Ollama API 설정
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')


def has_cjk(text):
    """한자, 히라가나, 가타카나 감지 (CJK 필터링)"""
    cjk_pattern = r'[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]'
    return bool(re.search(cjk_pattern, text))


def summarize_with_ollama(text, max_tokens=100):
    """Ollama를 사용하여 텍스트를 요약합니다."""
    try:
        prompt = f"""다음 텍스트를 반드시 한국어로만 요약하세요. 
절대로 영어나 다른 언어를 사용하지 마세요.
2-3개의 완전한 한국어 문장으로 핵심 내용을 요약하세요.

텍스트:
{text[:500]}

한국어 요약:"""
        
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


def generate_quiz_with_ollama(text):
    """Ollama를 사용하여 O/X 퀴즈 5개를 생성합니다. (Stage 1 MVP)"""
    try:
        prompt = f"""다음 글을 읽고 O/X 퀴즈 5개를 만드세요.

텍스트:
{text[:400]}

중요한 규칙:
1. 한국어로만 작성하세요 (한자, 외래어 금지)
2. 자연스러운 평서문으로 작성하세요
3. "~이다", "~한다", "~있다" 형태로 끝나야 합니다
4. 질문 형태(~인가?, ~할까?) 절대 금지

좋은 예시:
- "인공지능은 의료 분야에서 활용되고 있다"
- "딥러닝은 머신러닝의 한 종류이다"
- "파이썬은 프로그래밍 언어이다"

나쁜 예시:
- "인공지능은 의료에서 사용되는가?" (질문형)
- "AI는 醫療分野에서 활용된다" (한자 포함)

정확히 이 형식으로 작성:
1. [높음] 자연스러운 평서문 질문 | true
2. [중간] 자연스러운 평서문 질문 | false
3. [높음] 자연스러운 평서문 질문 | true
4. [낮음] 자연스러운 평서문 질문 | false
5. [중간] 자연스러운 평서문 질문 | true"""
        
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        response_text = result.get('response', '').strip()
        
        # 응답 파싱 - 줄 바꿈 정규화
        quiz_list = []
        normalized = ' '.join(response_text.split())
        # 패턴: "N. [importance] question | answer"
        pattern = r'(\d+)\.\s+\[([^\]]+)\]\s+([^|]+)\|\s*(true|false)'
        matches = re.findall(pattern, normalized, re.IGNORECASE)
        
        for match in matches:
            try:
                if len(match) == 5:
                    num, importance_part, question_part, answer_part, explanation_part = match
                else:
                    num, importance_part, question_part, answer_part = match[:4]
                    explanation_part = ''
                
                question_part = question_part.strip()
                answer_part = answer_part.lower()
                
                # 한자/외래어 필터링
                if has_cjk(question_part):
                    continue
                
                # 앞의 "질문1:", "질문2:" 같은 번호 제거
                question_part = question_part.lstrip('0123456789').lstrip(':. ').strip()
                
                if len(question_part) > 3:
                    difficulty = 1 if importance_part in ['낮음', 'low'] else (2 if importance_part in ['중간', 'medium'] else 3)
                    importance = importance_part if importance_part in ['높음', '중간', '낮음'] else 'high'
                    
                    answer_bool = answer_part in ['true']
                    explanation = explanation_part.strip() if explanation_part else '본문의 내용을 근거로 합니다.'
                    
                    quiz = {
                        'question': question_part,
                        'answer': answer_bool,
                        'difficulty': difficulty,
                        'importance': importance,
                        'explanation': explanation
                    }
                    quiz_list.append(quiz)
            except Exception:
                continue
        
        return quiz_list
    except Exception as e:
        print(f"Error: 퀴즈 생성 실패: {str(e)}", file=sys.stderr)
        return []


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
        print(f'HTML length: {len(html)}')
        
        # 2. 본문 추출
        title, text = extract_text(html, url=url)
        print(f'Extracted - Title: {title}, Text length: {len(text)}')
        
        # 3. Ollama로 요약
        print('Summarizing with Ollama...')
        summary = summarize_with_ollama(text)
        print(f'Summary: {summary[:100]}...')
        
        return jsonify({
            'url': url,
            'title': title,
            'text_length': len(text),
            'summary': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/quiz', methods=['POST'])
def quiz():
    """URL의 본문을 추출하고 퀴즈를 생성합니다."""
    try:
        data = request.json or {}
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'url required'}), 400
        
        html = fetch_html(url)
        title, text = extract_text(html, url=url)
        quiz_list = generate_quiz_with_ollama(text)
        
        return jsonify({
            'url': url,
            'title': title,
            'quiz_count': len(quiz_list),
            'quiz': quiz_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'Starting server on port {port}')
    print(f'Ollama host: {OLLAMA_HOST}, Model: {OLLAMA_MODEL}')
    app.run(host='0.0.0.0', port=port, debug=False)
