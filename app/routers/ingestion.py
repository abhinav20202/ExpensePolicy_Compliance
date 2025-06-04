from fastapi import APIRouter, UploadFile, File
from app.services.ingestion_service import (
   handle_expense_upload,
   # handle_receipt_ocr,
   # handle_policy_ingestion
)
from fastapi import APIRouter, UploadFile, File
# from app.services.ocr_service import process_receipt
# from app.services.policy_service import check_policy
# from app.services.report_service import generate_report

router = APIRouter()
@router.post("/expense")
async def upload_expense(file: UploadFile = File(...)):
   return await handle_expense_upload(file)

# @router.post("/receipt")
# async def upload_receipt(file: UploadFile = File(...)):
#    return await handle_receipt_ocr(file)

# @router.post("/policy")
# async def upload_policy(file: UploadFile = File(...)):
#    return await handle_policy_ingestion(file)
 
# @router.post("/upload-receipt/")
# async def upload_receipt(file: UploadFile = File(...)):
#     content = await file.read()
#     receipt_text = process_receipt(content)
#     return {"receipt_text": receipt_text}
 
# @router.get("/check-policy/")
# async def check_expense_policy():
#     violations = check_policy()
#     return {"violations": violations}
 
# @router.get("/generate-report/")
# async def generate_expense_report():
#     report_path = generate_report()
#     return {"report_path": report_path}

