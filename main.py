from PIL import Image
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from model.tag import get_tags_from_azure, classify_tags
from model.ui import detect_ui
from model.ocr import detect_text, classify_text


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

class annotateResponse(BaseModel):
    category: str
    tags: list[str]
    caption : list[str]
    

@app.post("/ai/annotate", response_model=annotateResponse)
def annotate_image(image_data: UploadFile = File(...)): 
   
    if not image_data.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    

    try:
        image = Image.open(image_data.file)
        image = image.copy()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid image file") from e
    finally:
        image_data.file.close()

    # Azure tagging
    tags = get_tags_from_azure(image)
    # extract str from tags for caption
    tags_str = ",".join(tags)
    
    # Google OCR
    extracted_text = detect_text(image)  
   
    category = classify_tags(tags)  # Step 1: Azure tagging 기반
    if category == "기타":
        category = detect_ui(image)  # Step 2: Roboflow UI Detection 기반
        if category == "기타":
            category = classify_text(extracted_text)  # Step 3: Google OCR 기반

    caption = [category, tags_str, extracted_text]
    
    
    return annotateResponse(
        category=category,
        tags=tags,
        caption=caption 
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=13131)
    
    