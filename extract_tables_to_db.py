import pdfplumber
import pandas as pd
import json
import re
import camelot
import tabula
from typing import Dict, List, Any

class PDFTableExtractor:
    def __init__(self):
        self.bio_fields = ['name', 'age', 'sex', 'file no', 'date']
        
    def extract_tables(self, pdf_path: str) -> List[pd.DataFrame]:
        """
        Extract tables using multiple methods for compatibility
        """
        tables = []
        
        # Try Camelot first (works best for structured PDFs)
        try:
            camelot_tables = camelot.read_pdf(pdf_path, pages='all')
            if len(camelot_tables) > 0:
                for table in camelot_tables:
                    tables.append(pd.DataFrame(table.data[1:], columns=table.data[0]))
                return tables
        except Exception as e:
            print(f"Camelot extraction failed: {e}")
        
        # Try Tabula as backup
        try:
            tabula_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            if len(tabula_tables) > 0:
                tables.extend(tabula_tables)
                return tables
        except Exception as e:
            print(f"Tabula extraction failed: {e}")
        
        # Use pdfplumber as final fallback
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted_tables = page.extract_tables()
                    for table in extracted_tables:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df)
        except Exception as e:
            print(f"PDFPlumber extraction failed: {e}")
        
        return tables

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names by converting to lowercase and removing special characters
        """
        df.columns = [str(col).strip().replace('\n', ' ').lower() for col in df.columns]
        return df

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove extra spaces, newlines, and trim all values in the dataframe
        """
        df = df.applymap(lambda x: str(x).strip().replace('\n', ' ').lower() if pd.notnull(x) else x)
        return df
    
    def extract_bio_data(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Extract bio information if available in the first table
        """
        bio_data = {field: "" for field in self.bio_fields}  # Default empty bio
        
        for field in self.bio_fields:
            matching_cols = [col for col in df.columns if field.lower() in col.lower()]
            if matching_cols and not df[matching_cols[0]].empty:
                bio_data[field] = str(df[matching_cols[0]].iloc[0]).lower()
                continue
                
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col]).lower()
                    if field.lower() in cell_value:
                        value = re.split(f"{field.lower()}:?", cell_value, flags=re.IGNORECASE)
                        if len(value) > 1:
                            bio_data[field] = value[1].strip().lower()
                            break
        
        return bio_data

    def process_test_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """
        Process test results dynamically from extracted tables
        """
        data = {}
        df = self.clean_dataframe(df)
        
        for _, row in df.iterrows():
            row_values = row.dropna().tolist()
            
            if len(row_values) >= len(df.columns):
                test_name = row_values[0].strip().lower()
                test_data = {df.columns[i]: row_values[i].strip().lower() for i in range(1, len(df.columns))}
                data[test_name] = test_data
        
        return data

    def extract_and_format(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main function to extract and process tables
        """
        tables = self.extract_tables(pdf_path)
        if not tables:
            raise Exception("No tables found in the PDF")
        
        result = {"bio": {field: "" for field in self.bio_fields}, "data": {}}
        
        # Process first table as bio if applicable
        first_table = self.clean_column_names(tables[0])
        first_table = self.clean_dataframe(first_table)
        bio_data = self.extract_bio_data(first_table)
        
        if any(value for value in bio_data.values()):
            result["bio"] = bio_data
        
        # Process remaining tables as test data
        for table in tables:
            table = self.clean_column_names(table)
            test_data = self.process_test_data(table)
            result["data"].update(test_data)
            
        return result

    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """
        Save extracted data to JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

# Example usage
def main():
    extractor = PDFTableExtractor()
    
    try:
        pdf_path = "C:/Users/ADEWOLE/Desktop/Kehinde/Pdf to database/A1 Office 1681237722892.pdf"
        output_json = "C:/Users/ADEWOLE/Desktop/Kehinde/Pdf to database/output.json"
        
        result = extractor.extract_and_format(pdf_path)
        extractor.save_to_json(result, output_json)
        
        print("Successfully extracted and saved data")
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()
