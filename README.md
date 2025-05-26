# Collec AI


## 목차

- [Collec AI](#collec-ai)
  - [목차](#목차)
- [COLLEC\_AI API Documentation](#collec_ai-api-documentation)
  - [기본 개요](#기본-개요)
  - [API 엔드포인트](#api-엔드포인트)
    - [POST `/ai/annotate`](#post-aiannotate)
      - [Request](#request)
      - [Response](#response)
      - [예외 처리](#예외-처리)
      - [동작 과정](#동작-과정)
      - [Example Request (cURL)](#example-request-curl)
      - [Example Response](#example-response)
  - [To Do](#to-do)


---

# COLLEC_AI API Documentation

COLLEC_AI API 서버는 업로드된 이미지를 분석하여 이미지의 **카테고리**, **캡션**, **태그** 정보를 반환합니다.  
내부적으로 Azure Tagging, Google OCR, Roboflow UI Detection, Captioning 등의 여러 모델/서비스를 사용합니다.

## 기본 개요

- **Framework:** FastAPI  
- **Port:** 8000 (기본)  
- **Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 환경설정


- **환경 변수:**  
  .env.example을 참고하여 .env 파일을 작성하세요.
  프로젝트 루트 디렉토리 아래에 google credential을 위한 json 파일을 저장하세요. 

- **의존성 설치:**
  ```bash
   python -m venv venv

   source venv/Scripts/activate # windows
   source venv/bin/activate # linux/mac

   pip install -r requirements.txt

   ```
- **main.py uvicorn 설정 확인:**
   ```bash
   # main.py

   uvicorn.run(app, host="0.0.0.0", port=8000)
    # host: "0.0.0.0"(외부 서빙) 또는 "localhost"(내부 테스트)
    # port: 적당한 범위의 숫자
   ```
- **API 서버 실행:**
   ```bash
   python main.py
   ```

- **API 테스트:**
   브라우저에서 [http://localhost:8000/docs](http://localhost:8000/docs) 에 접속하여 Swagger UI를 통해 API를 테스트할 수 있습니다. 

## API 엔드포인트

### POST `/ai/annotate`

업로드한 이미지를 분석하여 아래 정보를 포함하는 JSON 응답을 반환합니다.

#### Request

- **Method:** POST  
- **URL:** `/ai/annotate`  
- **Headers:**  
  - `Content-Type: multipart/form-data`  
- **Form Data:**  
  - `image_data` (file): 이미지 파일 
    - **주의:** `image_data`의 MIME 타입이 `image/` 로 시작해야 합니다.

#### Response

- **Status Code:** 200 OK  
- **Content-Type:** application/json  
- **Response Model:** `annotateResponse`

  | 필드       | 타입       | 설명 |
  | ---------- | ---------- | -------------------------------------------------------------- |
  | category   | `str`      | 이미지의 카테고리. 내부 로직(태그, UI, OCR 기반 분류)에 따라 결정됩니다. |
  | caption    | `str`      | 이미지에 대한 캡션. 
  | tags       | `list[str]`| Azure Tagging을 통해 감지된 태그 리스트. Confidence 임계값 이상인 태그만 포함됩니다. |

#### 예외 처리

- **400 Bad Request:**  
  업로드된 파일의 MIME 타입이 이미지가 아닌 경우  
  _Detail: "Uploaded file is not an image"_

- **401 Unauthorized:**  
  이미지 파일을 열거나 처리하는 중 문제가 발생한 경우  
  _Detail: "Invalid image file"_

#### 동작 과정

1. **이미지 검증 및 로드:**  
   - 업로드된 파일이 이미지인지 MIME 타입으로 확인합니다.  
   - PIL을 사용해 이미지를 열고 메모리 상에 복사하여 파일 객체와 분리합니다.

2. **Azure Tagging:**  
   - `get_tags_from_azure(image)` 함수를 통해 Azure 기반 태깅을 수행합니다.  
   - 태깅 결과에서 confidence가 특정 임계값 이상인 태그만 추출합니다.

3. **Google OCR:**  
   - `detect_text(image)` 함수를 통해 이미지 내 텍스트를 추출합니다.

4. **Captioning:**  
   - `get_caption(image)` 함수를 통해 이미지 캡션을 생성합니다.

5. **카테고리 결정:**  
   - `classify_tags(tags)`를 먼저 사용해 Azure 태깅 기반으로 카테고리를 결정합니다.  
   - 결과가 "기타"일 경우, `detect_ui(image)` (Roboflow UI Detection)로 재분류하고,  
   - 여전히 "기타"라면 `classify_text(extracted_text)` (OCR 기반)로 최종 카테고리를 결정합니다.

6. **응답:**  
   - 최종적으로 결정된 카테고리, 캡션, 태그 정보를 JSON 형식으로 반환합니다.

#### Example Request (cURL)

```bash
curl -X POST "http://localhost:8000/ai/annotate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image_data=@/path/to/your/image.jpg;type=image/jpeg"
```

#### Example Response

```json
{
  "category": "문서 & 정보",
  "tags": ["tag1", "tag2", "tag3"],
  "caption": ["This is a sample caption"]
}
```


