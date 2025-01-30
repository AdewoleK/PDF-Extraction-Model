import pdfplumber
import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///extracted_tables.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define database model
class ExtractedTable(Base):
    __tablename__ = "pdf_extracted_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    page = Column(Integer, nullable=False)
    table_index = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)  # JSON data stored as string

# Create database tables
Base.metadata.create_all(bind=engine)

def extract_tables_from_pdf(pdf_path):
    """
    Extracts tables from a PDF and stores them in JSON format & database.
    
    Args:
        pdf_path (str): Path to the PDF file.
    """
    extracted_data = []
    db_session = SessionLocal()

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for table_index, table in enumerate(tables):
                headers = [h.lower().strip() if h else f"column_{i}" for i, h in enumerate(table[0])]  # Convert headers to lowercase
                
                table_dict = {}

                for row in table[1:]:  # Iterate over data rows
                    main_key = row[0].strip().lower() if row[0] else "unknown"  # Convert to lowercase
                    table_dict[main_key] = {}

                    for i, cell in enumerate(row[1:], start=1):  # Start from second column
                        if i < len(headers):  
                            table_dict[main_key][headers[i]] = cell.strip().lower() if cell else ""  # Convert values to lowercase

                table_entry = {
                    "page": page_num + 1,
                    "table_index": table_index + 1,
                    "data": table_dict
                }
                extracted_data.append(table_entry)

                # Save to database
                db_table = ExtractedTable(
                    page=table_entry["page"],
                    table_index=table_entry["table_index"],
                    data=json.dumps(table_entry["data"])  # Convert dict to JSON string
                )
                db_session.add(db_table)

    db_session.commit()
    db_session.close()

    # Save extracted data as JSON
    output_json = "extracted_tables.json"
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)

    print(f"Extraction complete. Data saved to {output_json} and database.")

# Example Usage
pdf_path = "C:/Users/ADEWOLE/Desktop/Kehinde/Pdf to database/A1 Office 1681237722892.pdf"  # Replace with your actual PDF file path
extract_tables_from_pdf(pdf_path)
