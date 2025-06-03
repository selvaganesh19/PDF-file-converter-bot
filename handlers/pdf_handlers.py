import os
from dotenv import load_dotenv
from pdf2docx import Converter
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image

# Load environment variables
load_dotenv()

TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

POPPLER_PATH = os.getenv("POPPLER_PATH")
if not POPPLER_PATH:
    raise EnvironmentError("POPPLER_PATH not set in environment or .env!")

def convert_pdf_to_word(pdf_path: str) -> str:
    word_path = pdf_path.replace('.pdf', '.docx')
    cv = Converter(pdf_path)
    cv.convert(word_path, start=0, end=None)
    cv.close()
    return word_path

def split_pdf(pdf_path: str, pages: list = None) -> list:
    reader = PdfReader(pdf_path)
    output_dir = os.path.join(TEMP_DIR, "split_pages")
    os.makedirs(output_dir, exist_ok=True)

    if pages is None:
        pages = list(range(1, len(reader.pages) + 1))

    output_paths = []
    for page_num in pages:
        if 1 <= page_num <= len(reader.pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num - 1])
            output_path = os.path.join(output_dir, f"page_{page_num}.pdf")
            with open(output_path, "wb") as f_out:
                writer.write(f_out)
            output_paths.append(output_path)

    return output_paths

def image_to_pdf(image_path: str) -> str:
    image = Image.open(image_path)
    if image.mode == "RGBA":
        image = image.convert("RGB")
    pdf_path = image_path.rsplit('.', 1)[0] + "_converted.pdf"
    image.save(pdf_path, "PDF", resolution=100.0)
    return pdf_path

def merge_images_to_pdf(image_paths: list) -> str:
    sorted_paths = sorted(image_paths)  # Sort to maintain order
    images = []
    for img_path in sorted_paths:
        img = Image.open(img_path)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        images.append(img)

    pdf_path = os.path.join(TEMP_DIR, "merged_images.pdf")
    images[0].save(pdf_path, save_all=True, append_images=images[1:], format="PDF")
    return pdf_path

def pdf_to_images(pdf_path: str, all_pages: bool = False) -> list:
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    images = convert_from_path(
        pdf_path
    )

    image_paths = []
    for idx, image in enumerate(images):
        img_path = pdf_path.replace('.pdf', f'_page{idx + 1}.png')
        image.save(img_path, 'PNG')
        image_paths.append(img_path)

    return image_paths
