from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
import docx
from io import BytesIO
from app.core.azure_service_client import AzureOpenAIClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def embed_chunks(chunks):
    azure_service_client = AzureOpenAIClient()
    return [azure_service_client.generate_embedding(chunk) for chunk in chunks]

async def handle_policy_upload(file: UploadFile):
    try:
        file_bytes = await file.read()

        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf_bytes(file_bytes)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx_bytes(file_bytes)
        else:
            raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
      
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4", chunk_size=200, chunk_overlap=50, separators='\n\n'
        )

        chunks = text_splitter.split_text(text)
        chunk_vectors = embed_chunks(chunks)

        return {
            "status": "success",
            "chunk_count": len(chunks),
            "chunks": chunks,
            "chunk_vectors": chunk_vectors
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Policy file error: {str(e)}")
