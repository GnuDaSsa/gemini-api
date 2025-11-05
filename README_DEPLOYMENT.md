# 🌐 배포 가이드

## 옵션 1: Streamlit Community Cloud (추천) ⭐

### 장점
- ✅ 완전 무료
- ✅ 가장 쉬운 설정
- ✅ GitHub 자동 연동
- ✅ 커스텀 도메인 무료

### 배포 방법
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub로 로그인
3. "New app" 클릭
4. Repository: `GnuDaSsa/gemini-api`
5. Main file: `page10_gemini_test.py`
6. **Secrets 설정**:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
7. Deploy!

**배포 URL 예시**: `https://your-app.streamlit.app`

---

## 옵션 2: Hugging Face Spaces 🤗

### 장점
- ✅ 완전 무료
- ✅ GPU 지원
- ✅ ML 커뮤니티 친화적

### 배포 방법
1. [Hugging Face](https://huggingface.co) 계정 생성
2. 새 Space 만들기:
   - Space name: `pangyo-water-bill`
   - License: MIT
   - SDK: **Streamlit**
   - Visibility: Public
3. GitHub 리포지토리 연동:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/pangyo-water-bill
   git push hf main
   ```
4. **Secrets 설정** (Settings > Repository secrets):
   - Name: `GEMINI_API_KEY`
   - Value: your_api_key_here

**배포 URL 예시**: `https://huggingface.co/spaces/USERNAME/pangyo-water-bill`

---

## 옵션 3: Railway.app 🚂

### 장점
- ✅ $5/월 무료 크레딧
- ✅ 자동 HTTPS
- ✅ GitHub 자동 배포

### 배포 방법
1. [Railway.app](https://railway.app) 접속
2. GitHub로 로그인
3. "New Project" > "Deploy from GitHub repo"
4. 리포지토리 선택: `gemini-api`
5. **환경 변수 설정**:
   - `GEMINI_API_KEY`: your_api_key_here
6. **Start Command 설정**:
   ```
   streamlit run page10_gemini_test.py --server.port $PORT --server.address 0.0.0.0
   ```

**배포 URL 예시**: `https://your-app.up.railway.app`

---

## 옵션 4: Render.com 🎨

### 장점
- ✅ 무료 티어
- ✅ 자동 HTTPS
- ⚠️ 15분 비활성화 시 슬립

### 배포 방법
1. [Render.com](https://render.com) 접속
2. GitHub로 로그인
3. "New" > "Web Service"
4. 리포지토리 연결: `gemini-api`
5. 설정:
   - **Name**: pangyo-water-bill
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run page10_gemini_test.py --server.port $PORT --server.address 0.0.0.0`
6. **환경 변수**:
   - `GEMINI_API_KEY`: your_api_key_here

**배포 URL 예시**: `https://pangyo-water-bill.onrender.com`

---

## 📊 비교표

| 플랫폼 | 무료 | 설정 난이도 | 슬립 모드 | 속도 | 추천도 |
|--------|------|-------------|-----------|------|--------|
| **Streamlit Cloud** | ✅ | ⭐ 쉬움 | ❌ 없음 | 빠름 | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | ✅ | ⭐⭐ 보통 | ❌ 없음 | 빠름 | ⭐⭐⭐⭐ |
| **Railway** | ✅ $5/월 | ⭐⭐ 보통 | ❌ 없음 | 빠름 | ⭐⭐⭐ |
| **Render** | ✅ | ⭐⭐ 보통 | ⚠️ 15분 | 느림 | ⭐⭐ |

---

## ❌ 불가능한 옵션

### GitHub Pages
- ❌ **정적 사이트만 가능** (HTML/CSS/JS)
- ❌ Python 백엔드 실행 불가
- ❌ Streamlit 같은 동적 앱 불가

### Vercel/Netlify
- ❌ 주로 Node.js/정적 사이트용
- ❌ Python 앱 지원 제한적

---

## 🎯 추천

**가장 쉽고 안정적**: Streamlit Community Cloud  
**대안**: Hugging Face Spaces

둘 다 완전 무료이고, 설정이 간단하며, 슬립 모드가 없어서 항상 빠르게 접속 가능합니다!
