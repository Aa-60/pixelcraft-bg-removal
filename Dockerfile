FROM python:3.10-slim

# Install system dependencies for OpenCV/rembg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create models directory (BiRefNet model auto-downloads on first run)
RUN mkdir -p models

# Hugging Face Spaces requires port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
