from fastapi import UploadFile
from app.core.azure_service_client import AzureOpenAIClient
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image, UnidentifiedImageError
import io
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from app.core.config.config import Config
import os
from app.utils.receipt_extractdata import extract_receipt_id, extract_amount


form_recognizer_client = DocumentAnalysisClient(
    endpoint=Config.FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(Config.FORM_RECOGNIZER_API_KEY)
)

async def handle_receipt_batch(files: list[UploadFile]):
    print("Processing batch of receipt files...")
    azure_client = AzureOpenAIClient()
    results = []

    for file in files:  # Iterate over each UploadFile object in the list
        try:
            content = await file.read()  # Read the content of the file
            filename = file.filename  # Access the filename attribute
            print(f"Processing file: {filename}")

            if filename.endswith((".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", "jfif")):
                # Use Azure Form Recognizer to extract text and data
                print("Using Azure Form Recognizer to extract data...")
                poller = form_recognizer_client.begin_analyze_document(
                    model_id="prebuilt-receipt",  # Use the prebuilt receipt model
                    document=io.BytesIO(content)
                )
                document_analysis_result = poller.result()

                # Extract text and key-value pairs from the receipt
                extracted_data = []
                for document in document_analysis_result.documents:
                    for field_name, field in document.fields.items():
                        print(f"{field_name}: {field.value} (confidence: {field.confidence})")
                        if field.value:
                            extracted_data.append(f"{field_name}: {field.value} (confidence: {field.confidence})")

                receipt_id_field = document.fields.get("TransactionId")
                receipt_id = receipt_id_field.value if receipt_id_field and receipt_id_field.value else None
                amount_field = document.fields.get("Total")
                amount = amount_field.value if amount_field and amount_field.value else None
                print(f"Extracted Receipt_ID: {receipt_id}, Amount: {amount}")

                text = "\n".join(extracted_data)
                print("Combined Extracted text:\n", text)  # Log first 100 characters

            else:
                raise ValueError("Unsupported file format. Please upload PDF or image files.")

            if not text.strip():
                raise ValueError("No text detected in receipt.")
            chunks = chunk_text(text)
            print(f"Generated {chunks} chunks from extracted text.")
            print(filename)

            # Generate embedding
            chunk_embeddings = [azure_client.generate_embedding(chunk) for chunk in chunks]
            results.append({
                "filename": os.path.splitext(filename)[0],
                "amount": amount if amount else "Not Detected",
                "text": text.strip(),
                "embedding": chunk_embeddings
            })

        except Exception as e:
            results.append({
                #"filename": filename,
                "error": str(e)
            })

    return {
        "status": "success",
        "receipts_processed": len(results),
        "data": results
    }
# async def handle_receipt_batch(files: list[UploadFile]):
#     print("Processing batch of receipt files...")
#     azure_client = AzureOpenAIClient()
#     results = []

#     for file in files:
#         try:
#             content = await file.read()
#             filename = file.filename.lower()
#             text = ""
#             print(f"Processing file: {filename}")

#             if filename.endswith(".pdf"):
#                 # Try extracting text using PyMuPDF
#                 doc = fitz.open(stream=content, filetype="pdf")
#                 text = "\n".join(page.get_text() for page in doc)
#                 print(f"Extracted text from PDF: {text[:100]}...")  # Log first 100 characters

#                 # If no text found, fall back to OCR
#                 if not text.strip():
#                     images = convert_from_bytes(content)
#                     text = "\n".join(pytesseract.image_to_string(img) for img in images)

#             elif filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff","jfif")):
#                 image = Image.open(io.BytesIO(content)).convert("RGB")
#                 text = pytesseract.image_to_string(image)
#                 print(f"Extracted text from image: {text[:100]}...")  # Log first 100 characters

#             else:
#                 raise ValueError("Unsupported file format. Please upload PDF or image files.")

#             if not text.strip():
#                 raise ValueError("No text detected in receipt.")

#             # Generate embedding
#             embedding = azure_client.generate_embedding(text)

#             results.append({
#                 "filename": file.filename,
#                 "text": text.strip(),
#                 "embedding": embedding
#             })

#         except Exception as e:
#             results.append({
#                 "filename": file.filename,
#                 "error": str(e)
#             })

#     return {
#         "status": "success",
#         "receipts_processed": len(results),
#         "data": results
#     }
def chunk_text(text: str, chunk_size: int = 1000) -> list:
    """
    Splits the input text into smaller chunks of the specified size.

    Args:
        text: The input text to be chunked.
        chunk_size: The maximum size of each chunk.

    Returns:
        List of text chunks.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]