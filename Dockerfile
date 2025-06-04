FROM python:3.11-slim

# Install system packages
RUN apt-get update && apt-get install -y poppler-utils

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run your bot
CMD ["python", "bot.py"]
