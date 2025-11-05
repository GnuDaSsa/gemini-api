# Gemini Vision - 이미지 분석기 🧪

Gemini Pro Vision API를 활용한 이미지/PDF 분석 Streamlit 애플리케이션

## 기능

- 📸 이미지 업로드 (PNG, JPG, JPEG)
- 📄 PDF 파일 지원 (첫 페이지 자동 변환)
- 🤖 Gemini Pro Vision을 통한 자동 텍스트/정보 추출
- 💰 수도 요금 청구서 자동 분석
- 📊 연구소별 사용 요금 자동 계산

## 설치 방법

1. 저장소 클론
```bash
git clone <repository-url>
cd webapp
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 시스템 의존성 설치 (PDF 지원용)
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

4. API 키 설정
```bash
# gemini.env.example을 gemini.env로 복사
cp gemini.env.example gemini.env

# 파일을 열어 실제 API 키 입력
# GEMINI_API_KEY=your_actual_api_key_here
```

**API 키 발급**: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 받을 수 있습니다.

## 실행 방법

```bash
streamlit run page10_gemini_test.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

## 사용 방법

1. 이미지 또는 PDF 파일 업로드
2. 필요시 프롬프트 수정 (기본값: 수도 요금 청구서 분석용)
3. "Gemini로 분석" 버튼 클릭
4. 추출된 JSON 결과 및 계산된 요금 확인

## 보안 주의사항 ⚠️

- `gemini.env` 파일은 절대 Git에 커밋하지 마세요
- 이미 `.gitignore`에 포함되어 있습니다
- API 키가 노출되지 않도록 주의하세요

## 기술 스택

- Python 3.12
- Streamlit
- Google Generative AI (Gemini Pro Vision)
- pdf2image
- Pillow
- python-dotenv

## 라이선스

MIT License
