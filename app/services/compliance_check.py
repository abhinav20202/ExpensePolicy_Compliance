from sklearn.metrics.pairwise import cosine_similarity

def check_compliance(
    expense_vectors: list,
    receipt_vectors: list,
    policy_vectors: list,
    record_ids: list,
    receipt_flags: list,
    receipt_ids: list,
    receipt_names: list,
    expense_amounts: list,
    receipt_amounts: list,
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
        threshold: Similarity threshold for compliance.

    Returns:
        List of compliance results with explanations.
    """
    report = []

    for i, record_id in enumerate(record_ids):
        expense_vector = expense_vectors[i]
        receipt_attached = receipt_flags[i]
        receipt_id = receipt_ids[i] if i < len(receipt_ids) else None
        receipt_name = receipt_names[i] if i < len(receipt_names) else None
        receipt_amount = receipt_amounts[i] if i < len(receipt_amounts) else None
        expense_amount = expense_amounts[i] if i < len(expense_amounts) else None
        # receipt_vector = receipt_vectors[i] if receipt_attached else None
        receipt_vector = receipt_vectors[i] if receipt_attached and i < len(receipt_vectors) else None
       
        if receipt_attached:
        
            if receipt_name != receipt_id:
                report.append({
                    "Record_ID": record_id,
                    "Receipt_ID": receipt_id,
                    "Compliance": "Non-compliant",
                    "Explanation": f"Receipt name mismatch: Expected {receipt_id}, got {receipt_name}."
                })
                continue

            # Validate amount for the same receipt ID and name
            if receipt_amount != expense_amount:
                report.append({
                    "Record_ID": record_id,
                    "Receipt_ID": receipt_id,
                    "Compliance": "Non-compliant",
                    "Explanation": f"Amount mismatch for Receipt_ID {receipt_id} and Receipt_Name {receipt_name}: Expected {expense_amount}, got {receipt_amount}."
                })
                continue  

        # Compute similarity scores
        record_score = max(cosine_similarity([expense_vector], policy_vectors)[0])
        receipt_score = (
             max(cosine_similarity([receipt_vector], policy_vectors)[0])
             if receipt_vector else 0.0
        )

        # Determine compliance
        if not receipt_attached:
            compliance = "Non-compliant"
            explanation = "Receipt is missing, which violates the policy requirement."
        elif record_score < threshold: 
        # or receipt_score < threshold:
            compliance = "Non-compliant"
            explanation = (
                "The receipt or record does not align with the policy based on semantic similarity."
            )
        else:
            compliance = "Compliant"
            explanation = "The receipt and record align with the policy."

        report.append({
            "Record_ID": record_id,
            "Compliance": compliance,
            "Similarity_Score_Record": round(record_score, 3),
            "Similarity_Score_Receipt": round(receipt_score, 3),
            "Explanation": explanation
        })

    return report
