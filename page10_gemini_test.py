import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from pdf2image import convert_from_bytes
import json
from datetime import datetime
import glob

# Import ODT utilities
from odt_utils import (
    generate_water_bill_document,
    format_number_with_comma,
    number_to_korean
)

# --- Functions ---

def get_gemini_response(image, api_key, prompt):
    """
    Sends an image and a prompt to the Gemini Pro Vision model and returns the response.
    """
    if not api_key:
        st.error("Google AI Studio API 키를 입력해주세요.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Attempt to get more specific error information if available
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
            st.error(f"Prompt Feedback: {e.response.prompt_feedback}")
        return None

from dotenv import load_dotenv

# --- Streamlit App ---


def main():
    """
    Main function to run the Streamlit application.
    """
    # Load API key from gemini.env
    load_dotenv(dotenv_path='gemini.env')
    api_key = os.environ.get("GEMINI_API_KEY")

    st.set_page_config(page_title="판교 소부장 공동연구소 수도요금 자동화", page_icon="💧", layout="wide")
    st.title("💧 판교 소부장 공동연구소 수도요금 자동화 프로그램")
    st.markdown("""  
    수도 요금 청구서를 업로드하면 AI가 자동으로 정보를 추출하고 연구소별 요금을 계산합니다.  
    **제1연구소**와 **제2연구소**의 사용량에 따라 요금이 자동 배분됩니다.
    """)

    # --- Sidebar ---
    st.sidebar.title("📋 판교 소부장 공동연구소")
    st.sidebar.markdown("---")
    st.sidebar.info("🏢 **공동연구소 정보**")
    st.sidebar.markdown("""
    - 🔬 제1연구소
    - 🔬 제2연구소
    """)
    st.sidebar.markdown("---")
    st.sidebar.success("✅ 시스템 준비 완료")
    st.sidebar.caption("Powered by Google Gemini AI")

    # --- Main Content ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("📄 수도 요금 청구서 업로드")
        st.markdown("청구서 이미지 또는 PDF 파일을 업로드해주세요.")
        uploaded_file = st.file_uploader(
            "파일을 선택하거나 드래그하여 업로드",
            type=["png", "jpg", "jpeg", "pdf"],
            help="PNG, JPG, JPEG, PDF 형식을 지원합니다."
        )

        image_to_process = None
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                with st.spinner("PDF를 이미지로 변환 중..."):
                    images = convert_from_bytes(uploaded_file.read())
                    if images:
                        image_to_process = images[0]
                        st.image(image_to_process, caption="📄 업로드된 청구서 (PDF 첫 페이지)", use_column_width=True)
            else:
                image_to_process = Image.open(uploaded_file)
                st.image(image_to_process, caption="📄 업로드된 청구서", use_column_width=True)

    with col2:
        st.header("🤖 AI 분석 결과")
        if image_to_process is not None:
            with st.expander("⚙️ AI 분석 프롬프트 설정 (고급)", expanded=False):
                prompt = st.text_area(
                    "분석 프롬프트 (필요시 수정 가능):",
                '''이미지에서 다음 정보를 추출하여 JSON 형식으로 반환해주세요:
1. "due_date_amount": 납기 내 요금 (숫자만 추출)
2. "water_usage_m3": 상수도요금 사용량 (m³ 단위의 숫자만 추출)
3. "lab1_tons": 수기 메모에 있는 1연구소 사용량 (톤 단위의 숫자만 추출, 없으면 null)
4. "lab2_tons": 수기 메모에 있는 2연구소 사용량 (톤 단위의 숫자만 추출, 없으면 null)
5. "service_period": 사용기간 (예: "YYYY.MM.DD ~ YYYY.MM.DD")

만약 특정 필드를 찾을 수 없다면, 해당 필드의 값은 null로 설정해주세요.
''',
                    height=200
                )
            
            st.markdown("")
            if st.button("🚀 청구서 분석 시작", type="primary", use_container_width=True):
                with st.spinner("💡 AI가 청구서를 분석하고 있습니다... 잠시만 기다려주세요."):
                    response_text = get_gemini_response(image_to_process, api_key, prompt)
                    if response_text:
                        st.success("✅ 청구서 분석이 완료되었습니다!")
                        # Clean the response to extract only the JSON part
                        try:
                            # The model might return the JSON wrapped in ```json ... ```
                            json_str = response_text.strip().replace("```json", "").replace("```", "").strip()
                            parsed_json = json.loads(json_str)
                            
                            # Display extracted information in Korean
                            st.subheader("📊 청구서에서 추출된 정보")
                            
                            # Create a Korean-labeled dictionary
                            korean_labels = {
                                "due_date_amount": "총 금액",
                                "water_usage_m3": "총 사용량 (m³)",
                                "lab1_tons": "제1연구소 사용량 (톤)",
                                "lab2_tons": "제2연구소 사용량 (톤)",
                                "service_period": "사용기간"
                            }
                            
                            # Display in a more readable format
                            for key, korean_label in korean_labels.items():
                                value = parsed_json.get(key, "정보 없음")
                                if value is None:
                                    value = "정보 없음"
                                st.write(f"**{korean_label}**: {value}")
                            
                            st.divider()
                            
                            # Also show original JSON in an expander
                            with st.expander("원본 JSON 데이터 보기"):
                                st.json(parsed_json)

                            # --- Calculation Logic ---
                            st.markdown("---")
                            st.subheader("💰 연구소별 사용 요금 계산 결과")
                            try:
                                # Safely get values, defaulting to 0 if None or invalid
                                due_date_amount = float(parsed_json.get("due_date_amount") or 0)
                                water_usage_m3 = float(parsed_json.get("water_usage_m3") or 0)
                                lab1_tons = float(parsed_json.get("lab1_tons") or 0)
                                lab2_tons = float(parsed_json.get("lab2_tons") or 0)
                                service_period = parsed_json.get("service_period", "날짜 정보 없음")

                                if water_usage_m3 > 0:
                                    price_per_unit = due_date_amount / water_usage_m3
                                    lab1_fee = price_per_unit * lab1_tons
                                    lab2_fee = price_per_unit * lab2_tons

                                    # Truncate to the nearest 10 by using integer division
                                    lab1_fee_truncated = (int(lab1_fee) // 10) * 10
                                    lab2_fee_truncated = (int(lab2_fee) // 10) * 10

                                    col1, col2 = st.columns(2)
                                    
                                    # Display Lab 1 fee with formula
                                    with col1:
                                        st.metric(label="1연구소 사용요금", value=f"{lab1_fee_truncated:,} 원")
                                        st.caption(f"({due_date_amount:,.0f} / {water_usage_m3:,.0f}) × {lab1_tons:,.0f}")
                                    
                                    # Display Lab 2 fee with formula
                                    with col2:
                                        st.metric(label="2연구소 사용요금", value=f"{lab2_fee_truncated:,} 원")
                                        st.caption(f"({due_date_amount:,.0f} / {water_usage_m3:,.0f}) × {lab2_tons:,.0f}")
                                    
                                    st.info(f"📅 사용기간: {service_period}")
                                    
                                    # --- ODT 문서 생성 섹션 ---
                                    st.markdown("---")
                                    st.subheader("📝 공문 서식 자동 작성")
                                    
                                    # 템플릿 파일 찾기
                                    template_files = glob.glob("서식/*.odt")
                                    
                                    if template_files:
                                        st.info("✅ 서식 템플릿이 준비되어 있습니다. 아래 버튼을 클릭하여 공문을 생성하세요.")
                                        
                                        if st.button("📄 공문 서식 생성", type="secondary", use_container_width=True):
                                            with st.spinner("📝 공문 서식을 생성하는 중..."):
                                                template_path = template_files[0]
                                                
                                                # 출력 파일명 생성
                                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                                output_filename = f"수도요금부과_{timestamp}.odt"
                                                output_path = os.path.join("서식", output_filename)
                                                
                                                # ODT 파일 생성
                                                result = generate_water_bill_document(
                                                    template_path,
                                                    output_path,
                                                    parsed_json
                                                )
                                                
                                                if result["success"]:
                                                    st.success("✅ 공문 서식이 성공적으로 생성되었습니다!")
                                                    
                                                    # 치환된 내용 표시
                                                    with st.expander("📋 문서에 작성된 내용 확인"):
                                                        for key, value in result["replacements"].items():
                                                            st.write(f"**{key}**: {value}")
                                                    
                                                    # 파일 다운로드 버튼
                                                    with open(output_path, "rb") as file:
                                                        st.download_button(
                                                            label="💾 공문 서식 다운로드 (ODT)",
                                                            data=file,
                                                            file_name=output_filename,
                                                            mime="application/vnd.oasis.opendocument.text",
                                                            use_container_width=True
                                                        )
                                                else:
                                                    st.error(f"❌ 문서 생성 중 오류가 발생했습니다: {result.get('error', '알 수 없는 오류')}")
                                    else:
                                        st.warning("⚠️ 서식 템플릿 파일을 찾을 수 없습니다. '서식' 폴더에 ODT 템플릿 파일을 추가해주세요.")

                                else:
                                    st.warning("⚠️ 상수도 사용량이 0이므로 요금을 계산할 수 없습니다.")

                            except (ValueError, TypeError):
                                st.error("❌ 계산에 필요한 숫자 데이터가 없거나 잘못되었습니다. 추출된 정보를 확인해주세요.")
                            except Exception as e:
                                st.error(f"❌ 계산 중 예상치 못한 오류가 발생했습니다: {e}")


                        except json.JSONDecodeError:
                            st.error("❌ AI 응답 형식 오류가 발생했습니다. 원본 응답을 표시합니다.")
                            st.markdown(response_text)
                        except Exception as e:
                            st.error(f"❌ 오류가 발생했습니다: {e}")
                            st.markdown(response_text)
                    else:
                        st.warning("⚠️ 분석에 실패했습니다. 청구서를 다시 확인해주세요.")
        else:
            st.info("👆 왼쪽에서 수도 요금 청구서를 업로드하여 분석을 시작하세요.")

    # --- Instructions ---
    st.markdown("---")
    with st.expander("ℹ️ 프로그램 사용 방법"):
        st.markdown("""
        ### 📖 사용 방법
        
        1. **청구서 업로드**: 왼쪽 영역에서 수도 요금 청구서 파일을 업로드합니다.
           - 지원 형식: PNG, JPG, JPEG, PDF
        
        2. **분석 시작**: "🚀 청구서 분석 시작" 버튼을 클릭합니다.
        
        3. **결과 확인**: AI가 자동으로 다음 정보를 추출합니다:
           - 총 금액 (납기 내 요금)
           - 총 사용량 (m³)
           - 제1연구소 사용량 (톤)
           - 제2연구소 사용량 (톤)
           - 사용기간
        
        4. **요금 확인**: 각 연구소별 사용 요금이 자동으로 계산됩니다.
        
        ### 💡 주의사항
        - 청구서에 제1연구소와 제2연구소의 사용량이 **수기로 기재**되어 있어야 합니다.
        - 청구서 이미지가 선명할수록 정확도가 높아집니다.
        - 분석에 약 5-10초 정도 소요됩니다.
        """)

if __name__ == "__main__":
    main()