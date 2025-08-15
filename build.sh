#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Install system dependencies (for Render/Docker)
if command -v apt-get >/dev/null 2>&1; then
    echo "🔧 Installing system dependencies with apt-get..."
    apt-get update
    apt-get install -y \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        ghostscript \
        curl \
        || echo "⚠️ Some system packages failed to install"
elif command -v yum >/dev/null 2>&1; then
    echo "🔧 Installing system dependencies with yum..."
    yum update -y
    yum install -y \
        poppler-utils \
        tesseract \
        ghostscript \
        curl \
        || echo "⚠️ Some system packages failed to install"
else
    echo "⚠️ Package manager not found. Skipping system dependencies."
fi

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Check system tools availability
echo "🔍 Checking installed tools..."
if command -v pdftotext >/dev/null 2>&1; then
    echo "✅ pdftotext: $(which pdftotext)"
else
    echo "⚠️ pdftotext not available - using pdfplumber fallback"
fi

if command -v tesseract >/dev/null 2>&1; then
    echo "✅ tesseract: $(tesseract --version 2>&1 | head -1)"
else
    echo "⚠️ tesseract not available - OCR features disabled"
fi

if command -v gs >/dev/null 2>&1; then
    echo "✅ ghostscript: $(gs --version)"
else
    echo "⚠️ ghostscript not available - some PDF features may not work"
fi

echo "✅ Build completed successfully!"

# Make sure temp directories exist
mkdir -p temp_uploads uploads downloads

echo "📁 Created necessary directories"
echo "🎯 Build process completed. Ready to start server!"
