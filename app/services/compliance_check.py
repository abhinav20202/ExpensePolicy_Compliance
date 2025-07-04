# 
from app.core.azure_service_client import AzureOpenAIClient
from sklearn.metrics.pairwise import cosine_similarity
from openai import ChatCompletion
import numpy as np
import json
 
async def run_llm_compliance_check(record_data: dict, policy_chunks: list[str]) -> dict:
    """
    Runs an LLM compliance check for a given expense record and policy chunks.

    Args:
        record_data: Dictionary containing expense record details.
        policy_chunks: List of policy text chunks.

    Returns:
        Dictionary containing the compliance result and explanation.
    """
    azure_client = AzureOpenAIClient()
    prompt = f"""
You are an expense policy auditor. Given the following expense record and relevant policy terms, identify if any part of the record is non-compliant.
 
    Expense Record:
    {json.dumps(record_data, indent=2)}
    Policies:
    {json.dumps(policy_chunks, indent=2)}
    # Return one of:
    # - "Compliant"
    # - "Non-compliant: <reason and which policy is violated>"
    # """
    explanation =  azure_client.generate_completion(prompt)
    return {
        "record_id": record_data.get("receipt_id"),
        "compliance_result": explanation.strip()
    }
 
async def check_compliance(
    expense_vectors: list,
    receipt_vectors: list,
    policy_vectors: list,
    record_ids: list,
    receipt_flags: list,
    receipt_ids: list,
    receipt_names: list,
    expense_amounts: list,
    receipt_amounts: list,
    policy_chunks: list,
    categories: list,
    threshold: float = 0.8
) -> list:
    """
    Compares each expense record and its corresponding receipt (if attached)
    against the policy vectors using cosine similarity.

    Args:
        expense_vectors: List of embeddings for each expense record.
        receipt_vectors: List of embeddings for each receipt (same order as records).
        policy_vectors: List of policy chunk embeddings.
        record_ids: List of record IDs (e.g., EXP00001).
        receipt_flags: List of booleans indicating if a receipt is attached.
        receipt_ids: List of receipt IDs from the expense file.
        receipt_names: List of receipt names from the uploaded receipt images.
        expense_amounts: List of expense amounts from the expense file.
        receipt_amounts: List of receipt amounts extracted from the uploaded receipts.
        policy_chunks: List of policy text chunks.
        categories: List of categories for each expense record.
        threshold: Similarity threshold for compliance.

    Returns:
        List of compliance results with explanations.
    """
    report = []

    # Filter records to include only those with matching receipt IDs and receipt names
    matching_records = [
        i for i, receipt_id in enumerate(receipt_ids)
        if receipt_id in receipt_names
    ]

    print(f"Matching Records: {matching_records}")  # Debugging log

    for i in matching_records:
        expense_vector = expense_vectors[i]
        receipt_attached = receipt_flags[i]
        receipt_id = receipt_ids[i]
        expense_amount = expense_amounts[i]
        receipt_vector = receipt_vectors[receipt_names.index(receipt_id)] if receipt_attached else None
        receipt_name = receipt_id  # Since we are filtering by matching receipt IDs
        receipt_amount = receipt_amounts[receipt_names.index(receipt_id)] if receipt_attached else None
        policy_chunks = policy_chunks if policy_chunks else []
        category = categories[i] if categories and i < len(categories) else None

        print(f"Processing Record ID: {record_ids[i]} with Receipt ID: {receipt_id}")  # Debugging log

        # Check if all conditions match
        if receipt_attached and receipt_amount == expense_amount:
            # Prepare record_data for LLM compliance check
            record_data = {
                "receipt_id": receipt_id,
                "receipt_name": receipt_name,
                "receipt_amount": receipt_amount,
                "expense_amount": expense_amount,
                "categories": category
            }
            try:
                # Call the LLM compliance check function
                llm_result = await run_llm_compliance_check(record_data, policy_chunks)
                print(f"LLM Result: {llm_result}")  # Debugging log
                compliance_result = llm_result.get("compliance_result", "Error: No result returned")
            except Exception as e:
                llm_result = {"compliance_result": f"Error: {str(e)}"}
                compliance_result = f"Error: {str(e)}"
            report.append({
                "Record_ID": record_ids[i],
                "Receipt_ID": receipt_id,
                "Compliance": llm_result.get("compliance_result", "Error: No result returned").split(":")[0].strip(),
                "Explanation": llm_result.get("compliance_result", "Error: No result returned")
            })
        else:
            mismatches = []
            if not receipt_attached:
                mismatches.append("Receipt is not attached.")
            if receipt_amount != expense_amount:
                mismatches.append(f"Amount mismatch: Expected {expense_amount}, got {receipt_amount}.")
            report.append({
                "Record_ID": record_ids[i],
                "Receipt_ID": receipt_id,
                "Compliance": "Non-compliant",
                "Explanation": " | ".join(mismatches)
            })

    return report
# async def check_compliance(
#     expense_vectors: list,
#     receipt_vectors: list,
#     policy_vectors: list,
#     record_ids: list,
#     receipt_flags: list,
#     receipt_ids: list,
#     receipt_names: list,
#     expense_amounts: list,
#     receipt_amounts: list,
#     policy_chunks: list,
#     categories: list,
#     threshold: float = 0.8
# ) -> list:
#     """
#     Compares each expense record and its corresponding receipt (if attached)
#     against the policy vectors using cosine similarity.
 
#     Args:
#         expense_vectors: List of embeddings for each expense record.
#         receipt_vectors: List of embeddings for each receipt (same order as records).
#         policy_vectors: List of policy chunk embeddings.
#         record_ids: List of record IDs (e.g., EXP00001).
#         receipt_flags: List of booleans indicating if a receipt is attached.
#         threshold: Similarity threshold for compliance.
 
#     Returns:
#         List of compliance results with explanations.
#     """
#     report = []
 
#     for i, record_id in enumerate(record_ids):
#         expense_vector = expense_vectors[i]
#         receipt_attached = receipt_flags[i]
#         receipt_id = receipt_ids[i] if i < len(receipt_ids) else None
#         expense_amount = expense_amounts[i] if i < len(expense_amounts) else None
#         receipt_vector = receipt_vectors[i] if receipt_attached and i < len(receipt_vectors) else None
#         policy_chunks = policy_chunks if policy_chunks else []
#         category = categories[i] if categories and i < len(categories) else None
 
#         print(f"Record {i}: Category = {categories}")
#         print(f"Record {i}: Receipt ID = {receipt_id}")
 
#         # Compare each receipt_name and receipt_amount with the current record_id
#         receipt_matched = False
#         for j, receipt_name in enumerate(receipt_names):
#             receipt_amount = receipt_amounts[j] if j < len(receipt_amounts) else None  # Match receipt_amount with receipt_name
#             print(f"Comparing Record ID {record_id} with Receipt Name {receipt_name} and Receipt Amount {receipt_amount}")
#             if receipt_id == receipt_name:
#                 receipt_matched = True
#                 # Check if all conditions match
#                 if receipt_attached and receipt_amount == expense_amount:
#                     # Prepare record_data for LLM compliance check
#                     record_data = {
#                         "receipt_id": receipt_id,
#                         "receipt_name": receipt_name,
#                         "receipt_amount": receipt_amount,
#                         "expense_amount": expense_amount,
#                         "categories": category
#                     }
#                     try:
#                         # Call the LLM compliance check function
#                         llm_result = await run_llm_compliance_check(record_data, policy_chunks)
#                         print(f"LLM Result: {llm_result}")  # Debugging log
#                         compliance_result = llm_result.get("compliance_result", "Error: No result returned")
#                     except Exception as e:
#                         llm_result = {"compliance_result": f"Error: {str(e)}"}
#                         compliance_result = f"Error: {str(e)}"
#                     report.append({
#                         "Record_ID": record_id,
#                         "Receipt_ID": receipt_id,
#                         "Compliance": llm_result.get("compliance_result", "Error: No result returned").split(":")[0].strip(),
#                         "Explanation": llm_result.get("compliance_result", "Error: No result returned")
#                     })
#                     break
#                 else:
#                     mismatches = []
#                     if not receipt_attached:
#                         mismatches.append("Receipt is not attached.")
#                     if receipt_amount != expense_amount:
#                         mismatches.append(f"Amount mismatch: Expected {expense_amount}, got {receipt_amount}.")
#                     report.append({
#                         "Record_ID": record_id,
#                         "Receipt_ID": receipt_id,
#                         "Compliance": "Non-compliant",
#                         "Explanation": " | ".join(mismatches)
#                     })
#                     break
 
#         # If no receipt_name matches the record_id
#         if not receipt_matched:
#             report.append({
#                 "Record_ID": record_id,
#                 "Receipt_ID": receipt_id,
#                 "Compliance": "Non-compliant",
#                 "Explanation": f"No matching receipt found for Receipt ID {receipt_id}."
#             })
 
#     return report