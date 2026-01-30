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
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5')


def has_chinese_or_japanese(text):
    """중국어(한자) 또는 일본어(히라가나, 가타카나) 감지"""
    # 한자 (중국어)
    chinese_pattern = r'[\u4E00-\u9FFF]'
    # 히라가나, 가타카나 (일본어)
    japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF]'
    
    has_chinese = bool(re.search(chinese_pattern, text))
    has_japanese = bool(re.search(japanese_pattern, text))
    
    return has_chinese or has_japanese


def is_korean_text(text):
    """텍스트가 주로 한국어인지 확인 (한글 비율 체크)"""
    if not text:
        return False
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(re.findall(r'[가-힣a-zA-Z0-9]', text))
    if total_chars == 0:
        return False
    return (korean_chars / total_chars) > 0.3  # 한글이 30% 이상이면 OK


def summarize_with_ollama(text, max_tokens=100):
    """Ollama를 사용하여 텍스트를 요약합니다."""
    try:
        prompt = f"""[중요] 반드시 한국어로만 작성하세요. 중국어, 일본어, 영어 사용 금지!

다음 글의 핵심 내용을 한국어로 요약해주세요.

글:
{text[:800]}

규칙:
- 반드시 한국어로만 작성 (한글만 사용)
- 중국어(汉字), 일본어, 영어 절대 사용 금지
- 3-4문장으로 핵심 내용 정리
- 주요 개념과 결론 포함

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
    """Ollama를 사용하여 O/X 퀴즈 5개를 생성합니다."""
    try:
        prompt = f"""[필수 규칙]
1. 반드시 한국어로만 작성 (중국어, 일본어, 영어 금지)
2. 반드시 아래 글에 나온 내용만 사용 (글에 없는 내용 절대 금지)
3. 추측하거나 지어내지 말 것

글:
{text[:1000]}

위 글의 내용만을 바탕으로 O/X 퀴즈 5개를 만드세요.

형식:
1. [글에서 언급된 사실을 바탕으로 한 문장] | O | [글의 어느 부분에서 확인할 수 있는지]
2. [글의 내용을 살짝 틀리게 바꾼 문장] | X | [왜 틀린지, 글에서 실제로 뭐라고 했는지]
3. [글에서 언급된 사실을 바탕으로 한 문장] | O | [근거]
4. [글의 내용을 살짝 틀리게 바꾼 문장] | X | [왜 틀린지]
5. [글에서 언급된 사실을 바탕으로 한 문장] | O | [근거]

퀴즈:"""
        
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
        
        # 디버그: Ollama 응답 출력
        print(f'Ollama quiz response: {response_text[:500]}...')
        
        # 응답 파싱 - 해설 포함 패턴
        quiz_list = []
        
        # 패턴: "N. 문장 | O/X | 해설" 또는 "N. 문장 | O/X"
        pattern_with_explanation = r'(\d+)\.\s*([^|]+)\|\s*(O|X|true|false)\s*\|\s*([^\n]+)'
        pattern_without = r'(\d+)\.\s*([^|]+)\|\s*(O|X|true|false)'
        
        matches = re.findall(pattern_with_explanation, response_text, re.IGNORECASE)
        has_explanation = True
        
        if not matches:
            matches = re.findall(pattern_without, response_text, re.IGNORECASE)
            has_explanation = False
        
        print(f'Parsed {len(matches)} quiz items (with explanation: {has_explanation})')
        
        difficulties = ['높음', '중간', '낮음', '중간', '높음']
        
        for i, match in enumerate(matches[:5]):
            try:
                if has_explanation:
                    num, question_part, answer_part, explanation_part = match
                else:
                    num, question_part, answer_part = match
                    explanation_part = '본문의 내용을 참고하세요.'
                
                question_part = question_part.strip()
                answer_part = answer_part.upper().strip()
                explanation_part = explanation_part.strip()
                
                # 플레이스홀더 필터링
                if '문장내용' in question_part or '해설내용' in explanation_part:
                    continue
                
                # 중국어/일본어 포함 시 필터링
                if has_chinese_or_japanese(question_part) or has_chinese_or_japanese(explanation_part):
                    print(f'Filtered out non-Korean quiz: {question_part[:30]}...')
                    continue
                
                if len(question_part) > 5:
                    # O, TRUE = 정답, X, FALSE = 오답
                    is_true = answer_part in ['O', 'TRUE']
                    
                    quiz = {
                        'question': question_part,
                        'answer': is_true,
                        'difficulty': (i % 3) + 1,
                        'importance': difficulties[i] if i < len(difficulties) else '중간',
                        'explanation': explanation_part
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
