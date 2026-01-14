#!/usr/bin/env python3
import os
import requests
import json

OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')

# 테스트 텍스트
test_text = """인공지능(AI)은 최근 몇 년간 놀라운 발전을 이루었습니다. 
특히 대규모 언어 모델의 등장으로 자연어 처리 기술이 급속도로 발전하고 있습니다.
의료, 금융, 교육 등 다양한 분야에서 AI는 혁신을 일으키고 있습니다. 
그러나 윤리적 문제와 일자리 감소 등의 우려도 함께 제기되고 있습니다.
전문가들은 AI의 올바른 활용과 규제의 균형이 중요하다고 강조하고 있습니다."""

prompt = f"""다음 텍스트를 읽고 O/X 퀴즈 5개를 생각하세요.

텍스트: {test_text[:400]}

다음 형식으로만 답하세요 (한 줄에 하나씩, 질문은 한국어):
1. [높음] 질문1 | true
2. [중간] 질문2 | false
3. [높음] 질문3 | true
4. [낮음] 질문4 | false
5. [중간] 질문5 | true

답변:"""

print("=" * 60)
print("Ollama 응답 디버그")
print("=" * 60)
print(f"모델: {OLLAMA_MODEL}")
print(f"호스트: {OLLAMA_HOST}")
print(f"프롬프트 (처음 200자):\n{prompt[:200]}...\n")

response = requests.post(
    f'{OLLAMA_HOST}/api/generate',
    json={'model': OLLAMA_MODEL, 'prompt': prompt, 'stream': False},
    timeout=60
)
response.raise_for_status()
result = response.json()
response_text = result.get('response', '').strip()

print("=" * 60)
print("원본 응답:")
print("=" * 60)
print(response_text)
print("\n" + "=" * 60)
print("응답 분석:")
print("=" * 60)

lines = response_text.split('\n')
print(f"총 줄 수: {len(lines)}")
for i, line in enumerate(lines[:10], 1):
    print(f"[줄 {i}] {repr(line)}")

print("\n" + "=" * 60)
print("파싱 시도:")
print("=" * 60)

quiz_list = []
for i, line in enumerate(lines):
    line = line.strip()
    if not line or len(line) < 5:
        continue
    
    print(f"\n[줄 {i}] '{line}'")
    
    if '[' in line and ']' in line and '|' in line:
        try:
            importance_part = line[line.find('[')+1:line.find(']')].strip()
            question_part = line[line.find(']')+1:line.rfind('|')].strip()
            answer_part = line[line.rfind('|')+1:].strip().lower()
            
            print(f"  → importance: '{importance_part}'")
            print(f"  → question: '{question_part}'")
            print(f"  → answer: '{answer_part}'")
            
            if len(question_part) > 3 and answer_part:
                print(f"  ✅ 파싱 성공!")
                quiz_list.append({
                    'question': question_part,
                    'answer': answer_part in ['true', 'o', 'y', '맞음', '참']
                })
        except Exception as e:
            print(f"  ❌ 오류: {e}")
    else:
        print(f"  ✗ 형식 미맞음 ([ 또는 ] 또는 | 없음)")

print(f"\n총 파싱된 퀴즈: {len(quiz_list)}")
