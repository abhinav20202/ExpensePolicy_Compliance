from fastapi import UploadFile
from app.core.azure_service_client import AzureOpenAIClient
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image, UnidentifiedImageError
import io

async def handle_receipt_batch(files: list[UploadFile]):
    azure_client = AzureOpenAIClient()
    results = []

    for file in files:
        try:
            content = await file.read()
            filename = file.filename.lower()
            text = ""

            if filename.endswith(".pdf"):
                # Try extracting text using PyMuPDF
                doc = fitz.open(stream=content, filetype="pdf")
                text = "\n".join(page.get_text() for page in doc)

                # If no text found, fall back to OCR
                if not text.strip():
                    images = convert_from_bytes(content)
                    text = "\n".join(pytesseract.image_to_string(img) for img in images)

            elif filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff","jfif")):
                image = Image.open(io.BytesIO(content)).convert("RGB")
                text = pytesseract.image_to_string(image)

            else:
                raise ValueError("Unsupported file format. Please upload PDF or image files.")

            if not text.strip():
                raise ValueError("No text detected in receipt.")

            # Generate embedding
            embedding = azure_client.generate_embedding(text)

            results.append({
                "filename": file.filename,
                "text": text.strip(),
                "embedding": embedding
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {
        "status": "success",
        "receipts_processed": len(results),
        "data": results
    }
