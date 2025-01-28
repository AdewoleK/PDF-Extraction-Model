import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pandas as pd
import json

# Configure Tesseract OCR (ensure tesseract is installed and path is set)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to extract tables from PDF (basic approach using OCR)
def extract_tables(pdf_path):
    tables = []
    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf):
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_result = pytesseract.image_to_string(img, config='--psm 6')
            tables.append({"page": page_num + 1, "table": ocr_result})
    return tables

# Function to save extracted data to JSON
def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Main function to process PDFs in bulk
def process_pdfs(pdf_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    all_extracted_data = {}

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            
            # Extract tables
            table_data = extract_tables(pdf_path)
            all_extracted_data[pdf_file] = table_data

    # Save all extracted data to a JSON file
    output_file = os.path.join(output_folder, "extracted_tables.json")
    save_to_json(all_extracted_data, output_file)

# Example usage
if __name__ == "__main__":
    pdf_folder = "C:/Users/ADEWOLE/Desktop/Kehinde/Pdf to database/PDF"  # Folder containing PDFs
    output_folder = "extracted_tables"  # Folder to save extracted JSON data
    process_pdfs(pdf_folder, output_folder)
    print("Table extraction complete and data saved to JSON.")
