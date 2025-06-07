import os
from dotenv import load_dotenv
from pdf2docx import Converter
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import platform

# Load environment variables
load_dotenv()

TEMP_DIR = "downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

POPPLER_PATH = os.getenv("POPPLER_PATH") if platform.system() == "Windows" else None

def convert_pdf_to_word(pdf_path: str) -> str:
    word_path = pdf_path.replace('.pdf', '.docx')
    cv = Converter(pdf_path)
    cv.convert(word_path, start=0, end=None)
    cv.close()
    return word_path

def parse_page_range_text(text: str) -> list[list[int]]:
    page_groups = []

    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            start, end = map(int, part.split("-"))
            page_groups.append(list(range(start, end + 1)))
        else:
            page_groups.append([int(part)])

    return page_groups

def split_pdf(pdf_path: str, page_groups: list[list[int]]) -> list:
    reader = PdfReader(pdf_path)
    output_dir = os.path.join(TEMP_DIR, "split_pages")
    os.makedirs(output_dir, exist_ok=True)

    output_paths = []

    for idx, group in enumerate(page_groups):
        writer = PdfWriter()

        added_pages = set()

        for page_num in group:
            if page_num in added_pages:
                continue
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
                added_pages.add(page_num)
            else:
                raise ValueError(f"Page {page_num} is out of range.")

        if len(writer.pages) == 0:
            continue

        output_path = os.path.join(output_dir, f"split_group_{idx + 1}.pdf")
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
    sorted_paths = sorted(image_paths)
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
        pdf_path,
        first_page=1,
        last_page=num_pages if all_pages else 1,
        poppler_path=POPPLER_PATH
    )

    image_paths = []
    for idx, image in enumerate(images):
        img_path = pdf_path.replace('.pdf', f'_page{idx + 1}.png')
        image.save(img_path, 'PNG')
        image_paths.append(img_path)

    return image_paths

def merge_pdfs(pdf_paths: list) -> str:
    writer = PdfWriter()

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)

    merged_path = os.path.join(TEMP_DIR, "merged_pdfs.pdf")
    with open(merged_path, "wb") as f_out:
        writer.write(f_out)

    return merged_path

def reorder_pdf(pdf_path: str, new_order: list[int]) -> str:
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_num in new_order:
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])
        else:
            raise ValueError(f"Page {page_num} is out of range.")

    reordered_path = pdf_path.replace('.pdf', '_reordered.pdf')
    with open(reordered_path, "wb") as f_out:
        writer.write(f_out)

    return reordered_path

def compress_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    compressed_path = pdf_path.replace('.pdf', '_compressed.pdf')
    with open(compressed_path, "wb") as f_out:
        writer.write(f_out)

    return compressed_path
