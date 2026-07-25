import pdfplumber
import pandas as pd
import os

# Path to the PDF file
pdf_path = '34SBI.pdf'
# Output Excel file name
excel_path = '34SBI.xlsx'

# Extract text from PDF and convert to DataFrame
rows = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            for row in table:
                rows.append(row)
            print(table)

if rows:
    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False, header=False)
    print(f"Successfully converted '{pdf_path}' to '{excel_path}'")
else:
    print(f"No tables found in '{pdf_path}'. Conversion not performed.")
