import pandas as pd
from fastapi import UploadFile, HTTPException
from io import BytesIO
from app.core.azure_service_client import AzureOpenAIClient
from app.core.config.config import Config
from app.utils.parser import parse_expense_file

async def handle_expense_upload(file: UploadFile):
    try:
        file_bytes = await file.read()
        df = parse_expense_file(file_bytes, file.filename)

        azure_service_client = AzureOpenAIClient()
        record_vectors = []
        record_ids = []
        receipt_flags = []
        receipt_amounts = []
        receipt_ids=[]

        for _, row in df.iterrows():
            record_text = " ".join(map(str, row.values))
            embedding = azure_service_client.generate_embedding(record_text)
            record_vectors.append(embedding)
            record_ids.append(row["ID"])  # assuming 'ID' is the unique identifier
            receipt_flags.append(row.get("Receipt_Attached", False))  # assuming 'Receipt Flag' is optional
            receipt_amounts.append(row["Amount"])  # Assuming 'Amount' is the column name
            receipt_ids.append(row.get("Receipt_ID", None))  # Assuming 'Receipt_ID' is optional
        return {
            "status": "success",
            "record_count": len(record_vectors),
            "record_vectors": record_vectors,
            "record_ids": record_ids,
            "receipt_flags": receipt_flags,
            "receipt_amounts": receipt_amounts,
            "receipt_ids": receipt_ids
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Expense file error: {str(e)}")




# async def handle_expense_upload(file: UploadFile):
#     try:
#         # Read and parse the file using your parser
#         file_bytes = await file.read()
#         df = parse_expense_file(file_bytes, file.filename)
#         extracted_content = " ".join(df.astype(str).apply(lambda x: " ".join(x), axis=1))
        
#         # Simple character-based chunking
#         chunk_size = 800
#         chunks = [extracted_content[i:i+chunk_size] for i in range(0, len(extracted_content), chunk_size)]
#         print(chunks)
#         # Generate embeddings for each chunk
#         azure_service_client = AzureOpenAIClient()
#         chunk_vectors = []
#         for chunk in chunks:
#             print("entered the loop")
#             embedding = azure_service_client.generate_embedding(chunk)
#             chunk_vectors.append(embedding)
        
#         return {
#             "status": "success",
#             "chunk_count": len(chunks),
#             "chunks": chunks,
#             "chunk_vectors": chunk_vectors
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Expense file error: {str(e)}")
   

