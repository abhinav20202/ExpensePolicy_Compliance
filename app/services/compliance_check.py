from sklearn.metrics.pairwise import cosine_similarity

def check_compliance(
    expense_vectors: list,
    receipt_vectors: list,
    policy_vectors: list,
    record_ids: list,
    receipt_flags: list,
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
        receipt_vector = receipt_vectors[i] if receipt_attached else None

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
        elif record_score < threshold or receipt_score < threshold:
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
