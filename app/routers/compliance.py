from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.ingestion_service import handle_expense_upload
from app.services.policy_ingestion import handle_policy_upload
from app.services.receipt_service import handle_receipt_batch
from app.services.compliance_check import check_compliance

router = APIRouter()

@router.post("/check-compliance/")
async def check_compliance_api(
    expense_file: UploadFile = File(...),
    policy_file: UploadFile = File(...),
    receipt_files: List[UploadFile] = File(...)
):
    # Step 1: Get expense vectors
    expense_data = await handle_expense_upload(expense_file)
    print(f"Categories Data: {expense_data['categories']}")
    # Step 2: Get policy vectors
    policy_data = await handle_policy_upload(policy_file)
    
    # Step 3: Get receipt vectors
    receipt_data = await handle_receipt_batch(receipt_files)
    print(f"Receipt Data: {receipt_data}")

    receipt_vector =[r["embedding"] for r in receipt_data["data"]]
    print(f"Receipt Vectors: {receipt_vector}")

    # Step 4: Run compliance check
    report = await check_compliance(
        expense_vectors=expense_data["record_vectors"],
        receipt_vectors=[r["embedding"] for r in receipt_data["data"]],
        policy_vectors=policy_data["chunk_vectors"],
        record_ids=expense_data["record_ids"],
        receipt_flags=expense_data["receipt_flags"],
        receipt_ids=expense_data["receipt_ids"],
        # receipt_name = receipt_data["filename"],
        # receipt_names = receipt_data.get("filename", None),  # Use .get() to avoid KeyError
        receipt_names = [r["filename"] for r in receipt_data["data"]],
        expense_amounts=expense_data["receipt_amounts"],
        # receipt_amount=receipt_data["amounts"]
        receipt_amounts = [r["amount"] for r in receipt_data["data"]],  # Use .get() to avoid KeyError
        # receipt_amounts = receipt_data.get("amount", None)  # Use .get() to avoid KeyError
        policy_chunks=policy_data["chunks"],
        categories=expense_data['categories']   
    )

    return {"status": "success", "report": report}
#compliance