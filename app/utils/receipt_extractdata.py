import re

def extract_receipt_id(text: str) -> str:
    # Match "Receipt ID: <value>"
    match = re.search(r"Receipt\s*ID[:\s]+(\w+)", text, re.IGNORECASE)
    return match.group(1) if match else None

def extract_amount(text: str) -> float:
    # Adjusted regex to handle potential variations in formatting
    match = re.search(r"Amount[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    return float(match.group(1).replace(",", "")) if match else None