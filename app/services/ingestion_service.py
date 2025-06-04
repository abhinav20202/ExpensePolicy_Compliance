import pandas as pd
from fastapi import UploadFile, HTTPException
from io import BytesIO
from app.core.azure_service_client import AzureOpenAIClient
from app.core.config.config import Config
# import fitz  # PyMuPDF
# from paddleocr import PaddleOCR
# ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')  # You can replace with any OCR engine


async def handle_expense_upload(file: UploadFile):
    print("API Key:", Config.AZURE_OPENAI_API_KEY)  # Debug statement
    try:
        df = pd.read_csv(BytesIO(await file.read()))
        extracted_content = " ".join(df.astype(str).apply(lambda x: " ".join(x), axis=1))
        
        # Simple character-based chunking
        chunk_size = 800
        chunks = [extracted_content[i:i+chunk_size] for i in range(0, len(extracted_content), chunk_size)]
        print(chunks)
        # Generate embeddings for each chunk
        azure_service_client = AzureOpenAIClient()
        chunk_vectors = []
        for chunk in chunks:
            print("entered the loop")
            embedding = azure_service_client.generate_embedding(chunk)
            chunk_vectors.append(embedding)
        
        return {
            "status": "success",
            "chunks": chunks,
            "chunk_count": len(chunks),
            "chunk_vectors": chunk_vectors
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Expense file error: {str(e)}")
   
 
# def process_receipt(receipt_content: bytes) -> str:
#     images = convert_from_bytes(receipt_content)
#     text = " ".join(pytesseract.image_to_string(img) for img in images)
#     return text
 
# def process_image_file(image_path: str) -> str:
#     image = Image.open(image_path)
#     return pytesseract.image_to_string(image)



# async def handle_receipt_ocr(file: UploadFile):
#    try:
#        contents = await file.read()
#        with open(f"/tmp/{file.filename}", "wb") as f:
#            f.write(contents)
#        result = ocr_engine.ocr(f"/tmp/{file.filename}")
#        text = "\n".join([line[1][0] for block in result for line in block])
#        return {"status": "success", "text": text}
#    except Exception as e:
#        raise HTTPException(status_code=400, detail=f"OCR failed: {str(e)}")
# async def handle_policy_ingestion(file: UploadFile):
#    try:
#        contents = await file.read()
#        doc = fitz.open(stream=contents, filetype="pdf")
#        text = "\n".join([page.get_text() for page in doc])
#        # Placeholder: Do actual chunk + embed + Azure Search push
#        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
#        return {"status": "success", "chunks_stored": len(chunks)}
#    except Exception as e:
#        raise HTTPException(status_code=400, detail=f"Policy ingestion error: {str(e)}")