import os
import random
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from inference_sdk import InferenceHTTPClient

from utils import timing_decorator

load_dotenv()
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
API_URL = "https://detect.roboflow.com"
MODEL_NAME = "collec_250304/1"

def categorize_image(ui_classes):
    """
    UI detection 결과에 따라 카테고리를 지정
    """
    chat_keywords = {"chat_bubble"}
    music_keywords = {"forward button", "pause button", "play button", "rewind button", "shuffle"}
    coupon_keywords = {"barcode"}

    if ui_classes & chat_keywords:
        category = "대화기록"
    elif ui_classes & music_keywords:
        category = "노래"
    elif ui_classes & coupon_keywords:
        category = "쿠폰"
    else:
        category = "기타"
        
    return category


@timing_decorator
def detect_ui(image: Image.Image):
    """이미지를 받아서 roboflow ui detection 수행 후 특정 조건을 만족하면 반환

    Args:
        image (Image.Image): 이미지

    Returns:
        category (str): 예측된 카테고리
    """
    temp = [random.choice("0123456789") for _ in range(30)]
    temp = "".join(temp) + ".jpeg"

    os.makedirs("./data", exist_ok=True) 
    image_path = f"./data/" + temp
    image.save(image_path, format="JPEG", quality=80)
    
    CLIENT = InferenceHTTPClient(
        api_url=API_URL,
        api_key=ROBOFLOW_API_KEY
    )
    try:
        result = CLIENT.infer(image_path, model_id=MODEL_NAME)
    finally:
        os.remove(image_path)
    
    ui_classes = {prediction["class"] for prediction in result.get("predictions", [])}
    category = categorize_image(ui_classes)
    return category


