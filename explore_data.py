import pandas as pd
import sys

# Read the Excel file
file_path = "nsf-awards-export-2025-11-07.xlsx"

try:
    # Read the Excel file
    df = pd.read_excel(file_path)

    print("=" * 80)
    print("EXCEL FILE STRUCTURE")
    print("=" * 80)
    print(f"\nTotal rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\n" + "=" * 80)
    print("COLUMN NAMES")
    print("=" * 80)
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")

    print("\n" + "=" * 80)
    print("DATA TYPES")
    print("=" * 80)
    print(df.dtypes)

    print("\n" + "=" * 80)
    print("FIRST 3 ROWS (SAMPLE)")
    print("=" * 80)
    print(df.head(3).to_string())

    print("\n" + "=" * 80)
    print("BASIC STATISTICS")
    print("=" * 80)
    print(df.describe(include='all').to_string())

except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)
