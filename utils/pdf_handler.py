import pdfplumber
import os
from config import Config

class PDFHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = ""
    
    def extract_text(self):
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                self.text += page.extract_text()
        return self.text
    
    def extract_tables(self):
        with pdfplumber.open(self.file_path) as pdf:
            tables = []
            for page in pdf.pages:
                for table in page.extract_tables():
                    tables.append(table)
        return tables