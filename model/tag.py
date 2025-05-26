import io
import os
from PIL import Image
from dotenv import load_dotenv
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient

from utils import timing_decorator

# .env 파일 로딩
load_dotenv()

def azure_authenticate():
    SUBSCRIPTION_KEY = os.getenv("AZURE_COMPUTERVISION_KEY")
    ENDPOINT = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")
    computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(SUBSCRIPTION_KEY))
    return computervision_client

def compress_image_to_bytes(image: Image.Image, max_dimension=1024, quality=80) -> bytes:
    """
    PIL.Image.Image를 받아서 
    1. max_dimension보다 width나 height가 작으면 비율 맞춰 축소
    2. JPEG 압축
    3. 바이너리 데이터로 변환
    """
    if image.width > max_dimension or image.height > max_dimension:
        image.thumbnail((max_dimension, max_dimension))
    with io.BytesIO() as buffer:
        image.save(buffer, format="JPEG", quality=quality)
        compressed_bytes = buffer.getvalue()
    return compressed_bytes

@timing_decorator
def get_tags_from_azure(image: Image.Image) -> list[tuple[str, float]]:
    """
    image 받아서 compress 후 Azure 거쳐서 tag와 confidence 튜플의 리스트를 반환
    
    :param image: Image.Image 
    :return tags: list[tuple[str, float]]     # (tag_name, tag_confidence)
    """
    client = azure_authenticate()
    
    compressed_bytes = compress_image_to_bytes(image)
    tags_result = client.tag_image_in_stream(io.BytesIO(compressed_bytes))
    
    if len(tags_result.tags) == 0:
        tags = []
    else:
        tags = [tag.name for tag in tags_result.tags]
    
    return tags


def classify_tags(tags):
    shop_keywords = {
        "accessory", "bag", "clothing", "fashion", "fashion accessory",
        "luggage and bags", "fashion design", "dress", 
        "cosmetics", "footwear", "furniture", "online advertising"
    }
    place_keywords= {
        "sky", "outdoor", "cloud", "building", "lighthouse", "night", 
        "landmark", "city", "road", "mountain", "ground", "tree", "water", 
        "beach", "plant", "nature", "sunset", "crosswalk", "way", 
        "architecture", "street", "vehicle"
    }
    animal_keywords= {
        "indoor", "animal", "pet", "mammal", "dog", "cat", "hamster",
        "rodent", "rat", "bird", "small to medium-sized cats",
        "outdoor", "pigeon", "ground", "feather", "amphibian",
        "reptile", "terrier", "whiskers"
    }
    people_keywords= {
        "human face", "person", "woman", "man", "smile", "footwear",
        "girl", "boy", "group", "collage", "lip", "tooth", "eyelash",
        "wall", "hat"
    }
    tags = [tag.lower() for tag in tags]
    tags_set = set(tags)
    
    if tags_set & shop_keywords:
        category = "쇼핑 & 구매"
    elif tags_set & place_keywords:
        category = "장소"
    elif tags_set & animal_keywords:
        category = "동물"
    elif tags_set & people_keywords:
        category = "사람 & 인물"
    else:
        category = "기타"
    
    return category
    
    
