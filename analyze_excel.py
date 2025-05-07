import pandas as pd
import os
import json

def analyze_excel_file(file_path):
    try:
        # Get the excel file sheet names
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        result = {
            'file_name': os.path.basename(file_path),
            'sheets': {}
        }
        
        # Process each sheet
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)  # Read just first 5 rows for preview
            
            # Get column info
            columns = []
            for col in df.columns:
                col_info = {
                    'name': str(col),
                    'dtype': str(df[col].dtype)
                }
                columns.append(col_info)
            
            # Sample data (first 3 rows)
            sample_data = df.head(3).to_dict('records')
            
            result['sheets'][sheet_name] = {
                'columns': columns,
                'sample_data': sample_data,
                'total_rows': len(pd.read_excel(file_path, sheet_name=sheet_name))
            }
            
        return result
    except Exception as e:
        return {'error': str(e)}

# Analyze the first file
file1 = "/Users/bahadirkorkmazer/projects/smarteq/smarteq/api/excel/Movita_3566_HXV_Router_V4.1.xlsx"
result1 = analyze_excel_file(file1)
print("=" * 80)
print(f"Analysis of {os.path.basename(file1)}:")
print(json.dumps(result1, indent=2, ensure_ascii=False))
print("=" * 80)

# Analyze the second file
file2 = "/Users/bahadirkorkmazer/projects/smarteq/smarteq/api/excel/Çinden gelenler ve istenenler.xlsx"
result2 = analyze_excel_file(file2)
print(f"Analysis of {os.path.basename(file2)}:")
print(json.dumps(result2, indent=2, ensure_ascii=False))
print("=" * 80)
