# Use official Python slim image
FROM python:3.11-slim

# Install system packages required
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libmagic1 \
    tesseract-ocr \
    libreoffice && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
