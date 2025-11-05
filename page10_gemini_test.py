import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from pdf2image import convert_from_bytes
import json

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

    st.set_page_config(page_title="Gemini 이미지 분석기", page_icon="✨", layout="wide")
    st.title("🧪 Gemini Vision - 이미지 판독 테스트")
    st.markdown("Gemini Pro Vision 모델이 얼마나 잘 읽어내는지 이미지나 PDF를 업로드하여 확인해보세요.")

    # --- Sidebar for API Key (Now Removed) ---
    # The API key is now loaded automatically from the gemini.env file.
    st.sidebar.success("API 키가 로드되었습니다.")
    st.sidebar.info("이제 사용자는 API 키를 직접 입력할 필요가 없습니다.")

    # --- Main Content ---
    col1, col2 = st.columns(2)

    with col1:
        st.header("🖼️ 파일 업로드")
        uploaded_file = st.file_uploader(
            "이미지 또는 PDF 파일 선택",
            type=["png", "jpg", "jpeg", "pdf"]
        )

        image_to_process = None
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                with st.spinner("PDF를 이미지로 변환 중..."):
                    images = convert_from_bytes(uploaded_file.read())
                    if images:
                        image_to_process = images[0]
                        st.image(image_to_process, caption="업로드된 PDF의 첫 페이지", use_column_width=True)
            else:
                image_to_process = Image.open(uploaded_file)
                st.image(image_to_process, caption="업로드된 이미지", use_column_width=True)

    with col2:
        st.header("🤖 Gemini의 응답")
        if image_to_process is not None:
            prompt = st.text_area(
                "Gemini에게 보낼 프롬프트:",
                '''이미지에서 다음 정보를 추출하여 JSON 형식으로 반환해주세요:
1. "due_date_amount": 납기 내 요금 (숫자만 추출)
2. "water_usage_m3": 상수도요금 사용량 (m³ 단위의 숫자만 추출)
3. "lab1_tons": 수기 메모에 있는 1연구소 사용량 (톤 단위의 숫자만 추출, 없으면 null)
4. "lab2_tons": 수기 메모에 있는 2연구소 사용량 (톤 단위의 숫자만 추출, 없으면 null)
5. "service_period": 사용기간 (예: "YYYY.MM.DD ~ YYYY.MM.DD")

만약 특정 필드를 찾을 수 없다면, 해당 필드의 값은 null로 설정해주세요.
''',
                height=250
            )
            if st.button("Gemini로 분석", type="primary"):
                with st.spinner("Gemini가 이미지를 분석 중입니다..."):
                    response_text = get_gemini_response(image_to_process, api_key, prompt)
                    if response_text:
                        st.success("분석 완료!")
                        # Clean the response to extract only the JSON part
                        try:
                            # The model might return the JSON wrapped in ```json ... ```
                            json_str = response_text.strip().replace("```json", "").replace("```", "").strip()
                            parsed_json = json.loads(json_str)
                            
                            # Display extracted information in Korean
                            st.subheader("추출된 정보:")
                            
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
                            st.subheader("🔬 연구소별 예상 요금:")
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

                                else:
                                    st.warning("상수도 사용량이 0이므로 요금을 계산할 수 없습니다.")

                            except (ValueError, TypeError):
                                st.error("계산에 필요한 숫자 데이터가 없거나 잘못되었습니다. 추출된 JSON을 확인해주세요.")
                            except Exception as e:
                                st.error(f"계산 중 예상치 못한 오류가 발생했습니다: {e}")


                        except json.JSONDecodeError:
                            st.error("JSON 형식의 응답을 파싱하는 데 실패했습니다. 원본 응답을 표시합니다.")
                            st.markdown(response_text)
                        except Exception as e:
                            st.error(f"오류가 발생했습니다: {e}")
                            st.markdown(response_text)
                    else:
                        st.warning("분석에 실패했거나 텍스트를 반환하지 않았습니다.")
        else:
            st.info("분석을 시작하려면 파일을 업로드하세요.")

    # --- Instructions ---
    with st.expander("ℹ️ 사용 방법"):
        st.markdown("""
        1.  **API 키 받기**: [Google AI Studio](https://aistudio.google.com/app/apikey)로 이동하여 무료 API 키를 받으세요.
        2.  **키 입력**: 사이드바의 텍스트 상자에 API 키를 붙여넣으세요.
        3.  **파일 업로드**: 이미지 또는 PDF 파일을 드래그 앤 드롭하거나 선택하세요.
        4.  **분석**: "Gemini로 분석" 버튼을 클릭하세요.
        5.  **검토**: "Gemini의 응답" 섹션에서 결과를 확인하세요. 모델을 안내하기 위해 프롬프트를 변경할 수도 있습니다.
        """)

if __name__ == "__main__":
    main()