#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / 'app'))

from extract import extract_text

import requests
import json


def summarize_with_ollama(text, ollama_host='http://localhost:11434', model='llama2', max_chars=500):
    """Test Ollama summarization"""
    try:
        prompt = f"""다음 텍스트를 한국어로 2-3 문장으로 간결하게 요약하세요. 최대 100자 이내:

{text[:max_chars]}

요약:"""
        
        print(f"[요청] Ollama ({model})로 요약 중...", file=sys.stderr)
        response = requests.post(
            f'{ollama_host}/api/generate',
            json={'model': model, 'prompt': prompt, 'stream': False},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:
        print(f"[오류] Ollama 요청 실패: {e}", file=sys.stderr)
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
    print("=" * 50)
    print("[1단계] HTML에서 본문 추출")
    print("=" * 50)
    title, text = extract_text(test_html)
    print(f"제목: {title}")
    print(f"본문 (처음 200자):\n{text[:200]}...\n")
    
    # 2. Ollama 요약
    print("=" * 50)
    print("[2단계] Ollama로 요약")
    print("=" * 50)
    summary = summarize_with_ollama(text)
    
    if summary:
        print(f"요약:\n{summary}\n")
        
        # 결과 저장
        result = {
            'title': title,
            'text_length': len(text),
            'summary': summary
        }
        
        out_path = project_root / '.ollama_test.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"결과 저장됨: {out_path}")
        return 0
    else:
        print("Ollama 요약 실패 - Ollama 서버가 실행 중인지 확인하세요")
        print("  macOS: ollama serve")
        print("  또는 'ollama'를 백그라운드에서 실행")
        return 1


if __name__ == '__main__':
    sys.exit(main())
