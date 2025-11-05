# 💧 판교 소부장 공동연구소 수도요금 자동화 프로그램

Gemini Pro Vision API를 활용한 수도요금 청구서 자동 분석 및 공문 서식 생성 시스템

## 주요 기능

- 📸 청구서 이미지/PDF 업로드 (PNG, JPG, JPEG, PDF)
- 🤖 Gemini Pro Vision AI를 통한 자동 정보 추출
- 💰 제1연구소 및 제2연구소 사용량 자동 분석
- 📊 연구소별 사용 요금 자동 계산 (10원 단위 절사)
- 📝 ODT 공문 서식 자동 생성 (11개 항목 자동 치환)
- 🔢 한글 금액 자동 변환 (예: 7,080 → 칠천팔십)
- 📅 사용기간 및 납기일 자동 계산

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

## 🌐 Streamlit Cloud 배포 방법

### 1. Streamlit Community Cloud 가입
1. [Streamlit Community Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인

### 2. 앱 배포
1. "New app" 클릭
2. Repository: `GnuDaSsa/gemini-api` 선택
3. Branch: `main`
4. Main file path: `page10_gemini_test.py`
5. App URL 설정 (원하는 URL)

### 3. Secrets 설정 (중요!)
배포 전에 **Settings > Secrets**에서 API 키 추가:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

### 4. 배포 완료!
배포가 완료되면 `https://your-app-name.streamlit.app` 형식의 URL로 접속 가능합니다.

## 🔑 환경 변수 설정

로컬 실행: `gemini.env` 파일에 설정  
클라우드 배포: Streamlit Secrets에 설정

## 📦 생성된 ODT 문서 항목

서식 템플릿의 다음 항목들이 자동으로 치환됩니다:
- `[총요금]` - 납기 내 총 요금 (쉼표 포함)
- `[총사용량]` - 총 사용량 (m³)
- `[사용기간]` - 사용기간 (예: 2025. 6. 23. ~ 7. 22.)
- `[기준금액]` - 단위당 금액
- `[1연구소사용량]` - 제1연구소 사용량 (톤)
- `[2연구소사용량]` - 제2연구소 사용량 (톤)
- `[연구소사용량]` - 연구소 합계 사용량
- `[부과액]` - 계산된 부과액 (10원 단위 절사)
- `[부과액한글]` - 한글 금액 (예: 칠천팔십)
- `[사용기간월]` - 사용기간의 월
- `[사용기간월다음달말일]` - 다음달 말일

## 라이선스

MIT License
