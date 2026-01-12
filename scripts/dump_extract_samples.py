#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

# Ensure project root is importable
project_root = Path(__file__).resolve().parents[1]
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.extract import extract_text


SAMPLES = {
    "simple_html": """
    <html>
      <head><title>테스트 문서</title></head>
      <body>
        <div id=\"post-content\">
          <h1>문서 제목</h1>
          <p>첫 문단입니다.</p>
          <p>두 번째 문단입니다.</p>
        </div>
      </body>
    </html>
    """,

    "fallback_paragraphs": """
    <html>
      <head><title></title></head>
      <body>
        <p>하나.</p>
        <p>둘.</p>
        <p>셋.</p>
      </body>
    </html>
    """,
}


def main():
    results = {}
    for name, html in SAMPLES.items():
        title, text = extract_text(html)
        results[name] = {"title": title, "text": text}

    out_path = project_root / ".extract_samples.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Print concise output for quick verification
    for name, r in results.items():
        print(f"--- {name} ---")
        print("TITLE:", r["title"]) 
        print("TEXT:\n", r["text"]) 
        print()

    print(f"Wrote detailed results to: {out_path}")


if __name__ == '__main__':
    main()
