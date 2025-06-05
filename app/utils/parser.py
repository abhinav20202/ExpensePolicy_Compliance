import pandas as pd
import io

# Function to parse expense file
def parse_expense_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
        
        # Optional: validate required columns
        required_columns = {"Amount", "Date", "Category", "Description"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

        return df
    except Exception as e:
        raise ValueError(f"Failed to parse expense file: {str(e)}")

