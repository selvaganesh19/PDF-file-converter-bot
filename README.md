# 📄 PDF File Converter Bot 🤖

A powerful Telegram bot that helps users convert and manage PDF and Word documents seamlessly, right from their phones or desktop.

---

## 🚀 Features

- 🔁 **PDF → Word**
- 🔁 **Word → PDF**
- ✂️ **Split PDF** by custom page ranges (e.g., `1,3-5`)
- 🖼️ **Image → PDF** (Supports multiple images → single PDF)
- 📸 **PDF → Images** (Download all pages as PNGs or ZIP)
- 📱 Fully mobile compatible application
- 📂 Supports uploading documents and photos and Excel file directly in chat

---

## 🖼️ Screenshots

### 🔁 PDF to Word

Converts a PDF file into a Word document.

![PDF to Word](![Screenshot 2025-05-29 122840](https://github.com/user-attachments/assets/2a198f66-980e-40d6-9924-62eca2a7e4be)


---

### 🔁 Word to PDF

Converts a Word document into a PDF file.

![Word to PDF](![Screenshot 2025-05-29 122949](https://github.com/user-attachments/assets/3be363ad-d72d-4f43-bd72-0b3c02e95b3b)


---

### ✂️ Split PDF

Split specific pages from a PDF using a custom range like `1,3-5`.

![Split PDF](![Screenshot 2025-05-29 123151](https://github.com/user-attachments/assets/85f9d11a-f81e-420a-a6b9-b401a123c694)

![Split Output](![Screenshot 2025-05-29 124013](https://github.com/user-attachments/assets/a34cee60-34f2-4516-86b9-8031ca6a1d95)


---

### 🖼️ Image to PDF

Send multiple images and get back a single combined PDF.

![Image to PDF](![Screenshot 2025-05-29 124706](https://github.com/user-attachments/assets/697f56a8-1876-4ad6-aa96-5fed29fab570)



---

### 📸 PDF to Images

Converts all pages of a PDF into PNG images or sends them as a ZIP file.

![PDF to Images](![Screenshot 2025-05-29 123445](https://github.com/user-attachments/assets/78643dc0-0629-4c77-9e35-c27318eb5cdb)


---

## 🧠 Built With

- Python 3.10+
- python-telegram-bot v20+
- pdf2docx
- PyPDF2
- pdf2image
- Pillow (PIL)

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pdf-file-converter-bot.git
cd pdf-file-converter-bot

2. Create a virtual environment

python -m venv ilovepdf-env
.\ilovepdf-env\Scripts\activate  # On Windows
# source ilovepdf-env/bin/activate  # On macOS/Linux

3. Install dependencies

pip install -r requirements.txt

4. Add environment variables
Create a .env file:
  BOT_TOKEN=your-telegram-bot-token
  POPPLER_PATH=C:\\path\\to\\poppler\\bin
⚠️ You can download Poppler for Windows and set the correct path.

5. Run the bot

python bot.py

📁 Folder Structure

pdf-file-converter-bot/
├── bot.py                  # Main bot logic
├── handlers/
│   ├── pdf_handlers.py     # PDF-related functions
│   └── word_handlers.py    # Word-related functions
├── downloads/              # Temporary storage
├── requirements.txt
├── .env                    # Your secrets (ignored in .gitignore)
└── .gitignore


