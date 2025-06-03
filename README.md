# 📄 PDF File Converter Bot 🤖

A powerful Telegram bot that helps users convert and manage PDF and Word documents seamlessly, right from their phones or desktop.

---

## 🚀 Features

- 🔁 **PDF → Word**
- 🔁 **Word → PDF**
- ✂️ **Split PDF** by custom page ranges (e.g., `1,3-5`)
- 🖼️ **Image → PDF** (Supports multiple images → single PDF)
- 📸 **PDF → Images** (Download all pages as PNGs or ZIP)
- 📱 Fully mobile compatible
- 📂 Supports uploading documents and photos directly in chat

---

## 🖼️ Screenshots

### 🔁 PDF to Word

Converts a PDF file into a Word document.

![PDF to Word](![Screenshot 2025-05-29 122840](https://github.com/user-attachments/assets/50544bd4-32aa-4f84-a31a-58532a4c2fa2)
)

---

### 🔁 Word to PDF

Converts a Word document into a PDF file.

![Word to PDF](![Screenshot 2025-05-29 122949](https://github.com/user-attachments/assets/ea77c01e-c2a5-420c-b974-24d238c7393b)
)

---

### ✂️ Split PDF

Split specific pages from a PDF using a custom range like `1,3-5`.

![Split PDF](![Screenshot 2025-05-29 123151](https://github.com/user-attachments/assets/61df3929-4127-4ec1-94ba-a1d7710626c4)
)
![Split Output](![image](https://github.com/user-attachments/assets/e3506a7b-3752-46dd-aecf-270c8d1fad16)


---

### 🖼️ Image to PDF

Send multiple images and get back a single combined PDF.

![Image to PDF](![image](https://github.com/user-attachments/assets/d858a3ec-112b-49a0-b03d-14f4cc8b2f0c)


---

### 📸 PDF to Images

Converts all pages of a PDF into PNG images or sends them as a ZIP file.

![PDF to Images](![image](https://github.com/user-attachments/assets/910fb338-b11d-4f4e-a9eb-0e1be6ad3617)


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


