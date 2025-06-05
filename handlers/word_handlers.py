import os
import subprocess

def convert_word_to_pdf(docx_path):
    output_dir = os.path.dirname(docx_path)
    try:
        subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_path],
            check=True
        )
        pdf_path = docx_path.replace('.docx', '.pdf')
        return pdf_path
    except Exception as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e}")
