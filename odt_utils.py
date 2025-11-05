"""
ODT 파일 처리 및 한글 숫자 변환 유틸리티
"""
from odf import text, teletype
from odf.opendocument import load
import zipfile
import tempfile
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


def number_to_korean(number):
    """
    숫자를 한글로 변환하는 함수
    예: 6738 -> "육천칠백삼십팔"
    """
    if number == 0:
        return "영"
    
    # 한글 숫자
    units = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
    tens = ["", "십", "백", "천"]
    thousands = ["", "만", "억", "조"]
    
    def convert_under_10000(n):
        """만 단위 미만 숫자를 한글로 변환"""
        if n == 0:
            return ""
        
        result = []
        for i, digit in enumerate(str(n).zfill(4)):
            digit = int(digit)
            pos = 3 - i
            
            if digit == 0:
                continue
            
            # 1은 십, 백, 천 앞에서 생략
            if digit == 1 and pos > 0:
                result.append(tens[pos])
            else:
                result.append(units[digit] + tens[pos])
        
        return "".join(result)
    
    # 음수 처리
    if number < 0:
        return "마이너스 " + number_to_korean(abs(number))
    
    # 만 단위로 분리
    parts = []
    thousand_index = 0
    
    while number > 0:
        part = number % 10000
        if part > 0:
            parts.append(convert_under_10000(part) + thousands[thousand_index])
        number //= 10000
        thousand_index += 1
    
    return "".join(reversed(parts))


def format_number_with_comma(number):
    """
    숫자를 세자리마다 쉼표를 찍어 반환
    예: 6738 -> "6,738"
    """
    return f"{int(number):,}"


def parse_service_period(period_str):
    """
    사용기간 문자열을 파싱하여 시작일과 종료일을 반환
    예: "2025.06.23 ~ 2025.07.22" -> (datetime, datetime)
    """
    try:
        # 다양한 형식 지원
        period_str = period_str.replace(" ", "").strip()
        
        if "~" in period_str:
            start_str, end_str = period_str.split("~")
        elif "-" in period_str:
            start_str, end_str = period_str.split("-")
        else:
            raise ValueError("Invalid period format")
        
        # 날짜 파싱 (YYYY.MM.DD 형식)
        start_date = datetime.strptime(start_str.strip(), "%Y.%m.%d")
        end_date = datetime.strptime(end_str.strip(), "%Y.%m.%d")
        
        return start_date, end_date
    except Exception as e:
        print(f"Error parsing service period: {e}")
        return None, None


def get_month_from_period(period_str):
    """
    사용기간에서 월 숫자를 추출
    예: "2025.07.14 ~ 2025.07.29" -> 7
    """
    start_date, _ = parse_service_period(period_str)
    if start_date:
        return start_date.month
    return None


def get_next_month_last_day(period_str):
    """
    사용기간 다음 달의 말일을 반환
    예: "2025.07.14 ~ 2025.07.29" -> "2025. 8. 31."
    """
    start_date, _ = parse_service_period(period_str)
    if not start_date:
        return None
    
    # 다음 달 첫째 날
    next_month = start_date + relativedelta(months=1)
    
    # 다음 달의 마지막 날
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
    
    # 형식: "YYYY. M. D."
    return f"{next_month.year}. {next_month.month}. {last_day}."


def format_service_period(period_str):
    """
    사용기간을 지정된 형식으로 변환
    예: "2025.06.23~2025.07.22" -> "2025. 6. 23. ~ 2025. 7. 22."
    """
    start_date, end_date = parse_service_period(period_str)
    if not start_date or not end_date:
        return period_str
    
    # 형식: "YYYY. M. D. ~ YYYY. M. D."
    formatted = f"{start_date.year}. {start_date.month}. {start_date.day}. ~ {end_date.year}. {end_date.month}. {end_date.day}."
    return formatted


def replace_text_in_odt(template_path, output_path, replacements):
    """
    ODT 파일의 텍스트를 치환 (content.xml 직접 수정 방식)
    
    Args:
        template_path: 템플릿 ODT 파일 경로
        output_path: 출력 ODT 파일 경로
        replacements: 치환할 텍스트 딕셔너리 {찾을_텍스트: 바꿀_텍스트}
    """
    try:
        # 임시 디렉토리 생성
        import shutil
        
        # ODT 파일은 ZIP 파일이므로 직접 수정
        with zipfile.ZipFile(template_path, 'r') as zip_ref:
            # content.xml 읽기
            content_xml = zip_ref.read('content.xml').decode('utf-8')
            
            # 모든 치환 수행
            for search, replace in replacements.items():
                content_xml = content_xml.replace(search, str(replace))
            
            # 새 ODT 파일 생성
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                # 모든 파일을 새 ZIP에 복사
                for item in zip_ref.namelist():
                    if item == 'content.xml':
                        # 수정된 content.xml 추가
                        zip_out.writestr(item, content_xml.encode('utf-8'))
                    else:
                        # 나머지 파일은 그대로 복사
                        zip_out.writestr(item, zip_ref.read(item))
        
        return True
        
    except Exception as e:
        print(f"Error processing ODT file: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_water_bill_document(template_path, output_path, extracted_data):
    """
    추출된 데이터를 사용하여 수도요금 문서 생성
    
    Args:
        template_path: 템플릿 ODT 파일 경로
        output_path: 출력 ODT 파일 경로
        extracted_data: AI가 추출한 데이터 딕셔너리
    """
    try:
        # 데이터 추출
        total_amount = float(extracted_data.get("due_date_amount", 0))
        total_usage = float(extracted_data.get("water_usage_m3", 0))
        lab1_usage = float(extracted_data.get("lab1_tons", 0))
        lab2_usage = float(extracted_data.get("lab2_tons", 0))
        service_period = extracted_data.get("service_period", "")
        
        # 계산
        base_price = total_amount / total_usage if total_usage > 0 else 0
        lab_total_usage = lab1_usage + lab2_usage
        charged_amount = base_price * lab_total_usage
        
        # 10원 단위로 절삭
        charged_amount_truncated = (int(charged_amount) // 10) * 10
        
        # 사용기간 관련 정보
        service_month = get_month_from_period(service_period)
        next_month_last_day = get_next_month_last_day(service_period)
        formatted_period = format_service_period(service_period)
        
        # 한글 금액
        amount_korean = number_to_korean(charged_amount_truncated) + "원"
        
        # 치환할 내용 준비
        replacements = {
            "[총요금]": format_number_with_comma(total_amount),
            "[총사용량]": format_number_with_comma(total_usage),
            "[사용기간]": formatted_period,
            "[기준금액]": format_number_with_comma(round(base_price, 2)),
            "[1연구소사용량]": format_number_with_comma(lab1_usage),
            "[2연구소사용량]": format_number_with_comma(lab2_usage),
            "[연구소사용량]": format_number_with_comma(lab_total_usage),
            "[부과액]": format_number_with_comma(charged_amount_truncated),
            "[사용기간월]": str(service_month) if service_month else "",
            "[사용기간월다음달말일]": next_month_last_day if next_month_last_day else "",
            "[부과액한글]": amount_korean,
        }
        
        # ODT 파일 생성
        success = replace_text_in_odt(template_path, output_path, replacements)
        
        if success:
            return {
                "success": True,
                "replacements": replacements,
                "output_path": output_path
            }
        else:
            return {
                "success": False,
                "error": "ODT 파일 처리 중 오류 발생"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
