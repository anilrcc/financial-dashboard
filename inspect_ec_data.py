
import requests
import zipfile
import io
import pandas as pd

def inspect_zip_contents():
    url = "https://ec.europa.eu/economy_finance/db_indicators/surveys/documents/series/nace2_ecfin_2511/main_indicators_sa_nace2.zip"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            print("Files in ZIP:")
            for filename in z.namelist():
                print(f" - {filename}")
                
            # Let's try to read the first excel file found to see columns
            excel_files = [f for f in z.namelist() if f.endswith('.xlsx') or f.endswith('.xls')]
            if excel_files:
                target_file = excel_files[0]
                print(f"\nReading first 5 rows of {target_file}...")
                
                # Read file into memory
                with z.open(target_file) as f:
                    file_content = io.BytesIO(f.read())
                
                # Check sheet names
                xls = pd.ExcelFile(file_content)
                print("\nSheet names:", xls.sheet_names)
                
                # Parse the MONTHLY sheet
                df = pd.read_excel(file_content, sheet_name='MONTHLY', header=None)
                print(f"\nDataFrame Shape: {df.shape}")
                
                # Print a chunk of the dataframe to understand layout
                print("\nSlice of Data (Rows 0-10, Cols 0-10):")
                print(df.iloc[:10, :10])
                
                # Check Row 7 (EA) across more columns
                print("\nRow 7 (EA?):")
                print(df.iloc[7, :10])
                
                # Try to find date columns (formatted like dates or 1985-01 etc.)
                print("\nChecking Row 0 for potential dates:")
                print(df.iloc[0, :20])
                
            else:
                print("No Excel files found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_zip_contents()
