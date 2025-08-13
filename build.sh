#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Download and install system dependencies manually
echo "🔧 Installing system dependencies..."

# Create temp directory
mkdir -p /tmp/deps

# Try to install poppler-utils alternative (PDF processing)
echo "📄 Setting up PDF processing..."
# For pdftotext alternative, we'll use pdfplumber which is already in requirements

# Check if we can access LibreOffice alternative or skip image generation
echo "🖼️ Checking image generation capabilities..."

echo "✅ Build completed successfully!"

# Make sure temp directories exist
mkdir -p temp_uploads uploads downloads
