"""
Hugging Face Spaces용 진입점
page10_gemini_test.py를 import하여 실행
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

# 메인 앱 실행
from page10_gemini_test import main

if __name__ == "__main__":
    main()
