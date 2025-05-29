import os
from docx2pdf import convert

def convert_word_to_pdf(word_path: str) -> str:
    if not word_path.lower().endswith(('.doc', '.docx')):
        raise ValueError("Input file is not a Word document")

    output_pdf = word_path.rsplit('.', 1)[0] + ".pdf"
    # Convert the Word document to PDF
    convert(word_path, output_pdf)
    return output_pdf
