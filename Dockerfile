# Use official Python slim image
FROM python:3.11-slim

# Install system packages and Java (default-jre)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libmagic1 \
        libgl1-mesa-glx \
        tesseract-ocr \
        libreoffice \
        default-jre \
        fonts-dejavu \
        && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
