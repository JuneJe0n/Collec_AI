import io
import os
import re
from PIL import Image
from google.cloud import vision

from utils import timing_decorator


def clean_text(text: str) -> str:
    """Removes unnecessary newlines and spaces from OCR text"""
    text = re.sub(r'\s+', ' ', text)  # 연속된 공백 -> 단일 공백
    text = re.sub(r'([가-힣])(\d)', r'\1 \2', text)  # 한글 + 숫자 -> 사이에 공백 추가
    text = re.sub(r'(\d)([가-힣])', r'\1 \2', text)  # 숫자 + 한글 -> 사이에 공백 추가
    text = re.sub(r'([a-zA-Z])([가-힣])', r'\1 \2', text)  # 영문 + 한글 -> 사이에 공백 추가
    text = re.sub(r'([가-힣])([a-zA-Z])', r'\1 \2', text)  # 한글 + 영문 -> 사이에 공백 추가
    return text.strip()  # 앞뒤 공백 제거

@timing_decorator
def detect_text(image: Image.Image) -> str:
    """
    :params image(Image.Image): 입력 이미지
    :return ocr_text(str): OCR 완료된 텍스트
    """
    client = vision.ImageAnnotatorClient()
    with io.BytesIO() as buffer:
        image.save(buffer, format="JPEG", quality=80)
        content = buffer.getvalue() 
        
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    text_info = response.text_annotations
    
    if response.error.message:
        raise Exception(f"Errors in OCR: {response.error.message}")
    
    descriptions = [(text.description).strip() for text in text_info]
    raw_text = ' '.join(descriptions)
    ocr_text = clean_text(raw_text)

    return ocr_text


def classify_text(text: str, threshold = 800):
    """
    Classify img based on text length and keywords
    """
    booking_keywords = ["예약", "예매", "티켓", "거래", "주문", "내역", "신용", "체크"]
    if len(text) >= threshold :
        category = "문서 & 정보"
    elif any(keyword in text for keyword in booking_keywords):
        category = "예약 & 거래"
    else:
        category = "기타"
        
    return category



