from typing import List
from fastapi import APIRouter, UploadFile, File
from app.services.ingestion_service import (
   handle_expense_upload,
   # handle_receipt_ocr,
   # handle_policy_ingestion
)
from app.services.policy_ingestion import handle_policy_upload
from app.services.receipt_service import handle_receipt_batch

from fastapi import APIRouter, UploadFile, File

# from app.services.ocr_service import process_receipt
# from app.services.policy_service import check_policy
# from app.services.report_service import generate_report

router = APIRouter()
@router.post("/expense")
async def upload_expense(file: UploadFile = File(...)):
   print("request Reached")
   return await handle_expense_upload(file)



@router.post("/policy")
async def upload_policy(file: UploadFile = File(...)):
   return await handle_policy_upload(file)
 
 
@router.post("/receipts")
async def upload_receipts(file: UploadFile = File(...)):  # Accept a single file
    print("Processing receipt upload...")
    return await handle_receipt_batch([file])  # Pass the file directly
 




