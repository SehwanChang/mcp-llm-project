#!/usr/bin/env python3
import os
import sys
import json
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'app'))

from extract import extract_text
import requests

OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')


def has_cjk(text):
    """한자/한글 외 CJK 문자 포함 여부 확인"""
    # 한자: U+4E00 ~ U+9FFF
    # 히라가나: U+3040 ~ U+309F
    # 가타카나: U+30A0 ~ U+30FF
    cjk_pattern = re.compile('[\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]')
    return cjk_pattern.search(text) is not None


def generate_quiz_with_ollama(text):
    """Ollama를 사용하여 O/X 퀴즈를 생성합니다. (Stage 1 MVP)"""
    try:
        # Stage 1 MVP: 구체적인 예시 포함, 매우 엄격한 형식 강제
        prompt = f"""다음 글을 읽고 O/X 퀴즈 5개를 만드세요.
글: {text[:300]}

한국어로만 된 단호한 문장 형식으로 만드세요.
예시: "인공지능은 의료에서 발전하고 있다." (O)
다른 예: "AI는 일자리를 감소시킨다." (X)

정확히 이 형식으로만 작성하세요:
1. [높음] 질문 | true
2. [중간] 질문 | false
3. [높음] 질문 | true
4. [낮음] 질문 | false
5. [중간] 질문 | true"""
        
        print(f"[요청] Ollama ({OLLAMA_MODEL})로 퀴즈 생성 중...", file=sys.stderr)
        response = requests.post(
            f'{OLLAMA_HOST}/api/generate',
            json={'model': OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        response_text = result.get('response', '').strip()
        
        print(f"[디버그] 응답 길이: {len(response_text)}", file=sys.stderr)
        
        # 응답 파싱 - 줄 바꿈 정규화
        quiz_list = []
        normalized = ' '.join(response_text.split())
        # 패턴: "N. [importance] question | answer"
        pattern = r'(\d+)\.\s+\[([^\]]+)\]\s+([^|]+)\|\s*(true|false)'
        matches = re.findall(pattern, normalized, re.IGNORECASE)
        
        print(f"[디버그] 정규표현식 매칭: {len(matches)}", file=sys.stderr)
        
        for match in matches:
            try:
                if len(match) == 5:
                    num, importance_part, question_part, answer_part, explanation_part = match
                else:
                    num, importance_part, question_part, answer_part = match[:4]
                    explanation_part = ''
                
                # 한자/외래어 필터링
                if has_cjk(question_part):
                    print(f"[필터] 한자 포함으로 스킵: {question_part[:30]}...", file=sys.stderr)
                    continue
                
                question_part = question_part.strip()
                answer_part = answer_part.lower()
                
                # 앞의 "질문1:", "질문2:" 같은 번호 제거
                question_part = question_part.lstrip('0123456789').lstrip(':. ').strip()
                
                if len(question_part) > 3:
                    difficulty = 1 if importance_part in ['낮음', 'low'] else (2 if importance_part in ['중간', 'medium'] else 3)
                    importance = importance_part if importance_part in ['높음', '중간', '낮음'] else 'high'
                    answer_bool = answer_part in ['true']
                    
                    quiz = {
                        'question': question_part,
                        'answer': answer_bool,
                        'difficulty': difficulty,
                        'importance': importance,
                        'explanation': '본문의 내용을 근거로 합니다.'
                    }
                    quiz_list.append(quiz)
                    print(f"[파싱 성공] {importance} | {question_part[:30]}...", file=sys.stderr)
            except Exception as e:
                print(f"[경고] 매칭 파싱 실패: {e}", file=sys.stderr)
                continue
        
        return quiz_list
    except Exception as e:
        print(f"[오류] 퀴즈 생성 실패: {e}", file=sys.stderr)
        return None


def main():
    # 테스트용 HTML
    test_html = """
    <html>
      <head><title>인공지능의 미래</title></head>
      <body>
        <article>
          <h1>인공지능이 세상을 바꾸고 있습니다</h1>
          <p>인공지능(AI)은 최근 몇 년간 놀라운 발전을 이루었습니다. 
          특히 대규모 언어 모델의 등장으로 자연어 처리 기술이 급속도로 발전하고 있습니다.</p>
          <p>의료, 금융, 교육 등 다양한 분야에서 AI는 혁신을 일으키고 있습니다. 
          그러나 윤리적 문제와 일자리 감소 등의 우려도 함께 제기되고 있습니다.</p>
          <p>전문가들은 AI의 올바른 활용과 규제의 균형이 중요하다고 강조하고 있습니다.</p>
        </article>
      </body>
    </html>
    """
    
    # 1. 추출
    print("=" * 60)
    print("[1단계] HTML에서 본문 추출")
    print("=" * 60)
    title, text = extract_text(test_html)
    print(f"제목: {title}")
    print(f"본문 (처음 150자):\n{text[:150]}...\n")
    
    # 2. 퀴즈 생성
    print("=" * 60)
    print("[2단계] Ollama로 퀴즈 생성")
    print("=" * 60)
    quiz_list = generate_quiz_with_ollama(text)
    
    if quiz_list is None:
        print("⚠️  퀴즈 생성 실패 - Ollama 서버가 실행 중인지 확인하세요")
        print("    Stage 1 MVP: Ollama 서버 문제")
        print("    Stage 2: 다른 모델 시도 또는 구조화된 출력 라이브러리 사용")
        return 1
    
    if len(quiz_list) == 0:
        print("⚠️  생성된 퀴즈가 없습니다.")
        print("    Stage 1 MVP: Ollama 응답 형식 파싱 실패")
        print("    Stage 2: JSON 파싱 개선 또는 간단한 CSV 형식 사용")
        return 1
    
    print(f"\n✅ {len(quiz_list)}개의 퀴즈 생성됨\n")
    
    # 3. 결과 출력
    for i, quiz in enumerate(quiz_list, 1):
        print(f"[문제 {i}] (난이도: {quiz.get('difficulty', '?')}, 중요도: {quiz.get('importance', '?')})")
        print(f"  질문: {quiz.get('question', '?')}")
        print(f"  정답: {'O' if quiz.get('answer') else 'X'}")
        print(f"  설명: {quiz.get('explanation', '?')}")
        print()
    
    # 4. 결과 저장
    result = {
        'title': title,
        'text_length': len(text),
        'quiz_count': len(quiz_list),
        'quiz': quiz_list
    }
    
    out_path = project_root / '.quiz_test.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"결과 저장됨: {out_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
