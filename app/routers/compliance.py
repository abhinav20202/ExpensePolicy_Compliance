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

    # Step 2: Get policy vectors
    policy_data = await handle_policy_upload(policy_file)

    # Step 3: Get receipt vectors
    receipt_data = await handle_receipt_batch(receipt_files)

    # Step 4: Run compliance check
    report = check_compliance(
        expense_vectors=expense_data["record_vectors"],
        receipt_vectors=[r["embedding"] for r in receipt_data["data"]],
        policy_vectors=policy_data["chunk_vectors"],
        record_ids=expense_data["record_ids"],
        receipt_flags=expense_data["receipt_flags"]
    )

    return {"status": "success", "report": report}
#compliance