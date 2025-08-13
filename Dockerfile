FROM python:3.9-slim

# Install system dependencies including poppler-utils for pdftotext
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libreoffice \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads downloads temp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Start command
CMD ["python", "web_server.py"]
