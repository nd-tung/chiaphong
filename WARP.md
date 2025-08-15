# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Hotel Room Classification System (chialich)** is a Flask web application that processes hotel PDF files to automatically generate housekeeping Excel reports. The system extracts room numbers from ARR (Arrivals), DEP (Departures), and GIH (Guests in House) PDF files and marks appropriate columns in a pre-defined Excel template.

## Architecture

### Core Components

1. **Flask Web Application** (`web_server.py`, `app.py`) - Main web interface with PDF upload and processing
2. **PDF Text Extraction** - Multi-approach PDF processing using `pdfplumber`, `pytesseract` OCR, and fallback methods
3. **Excel Template System** - Uses a predefined `template.xlsx` file with 133 pre-configured rooms
4. **Room Classification Logic** - Sophisticated business logic for categorizing rooms by check-in/out dates
5. **Image Generation Pipeline** - Excel → PDF → PNG conversion using ComPDF API and pdf2image
6. **Command-Line Interface** (`master_room_classifier.py`) - Standalone processing for batch operations

### Processing Flow

```
PDF Files → Text Extraction → Room Number Parsing → Classification Logic → Excel Template Update → Image Generation
```

### Key Business Logic

- **ARR Rooms**: Check-in on schedule date → Mark "X" in ARR column
- **DEP Rooms**: Check-out on schedule date → Mark "X" in DO column  
- **GIH OD Rooms**: Staying overnight (not checking in/out) → Mark "X" in OD column
- **Date Filtering**: Uses schedule date (DD-MM-YY format) for classification
- **Template Mapping**: Finds room numbers in template and marks corresponding columns

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Build with system dependencies (for deployment)
bash build.sh
```

### Running the Application

```bash
# Development server (port 8000)
python3 web_server.py

# Alternative with different port
python3 run.py  # Uses port 5000

# Using app.py directly
python3 app.py

# Production with Gunicorn
gunicorn -c gunicorn.conf.py web_server:app
```

### Command Line Processing
```bash
# Run standalone classifier (interactive)
python3 master_room_classifier.py

# Test with sample files
python3 test_simple.py  # If exists
```

### Docker Deployment
```bash
# Build Docker image
docker build -t chialich .

# Run container
docker run -p 8000:8000 chialich
```

## Key Files and Directories

- **`template.xlsx`** - Critical Excel template with 133 room layout (DO NOT modify structure)
- **`web_server.py`** - Main Flask application with full feature set
- **`app.py`** - Alternative/simplified Flask app
- **`master_room_classifier.py`** - Command-line processing tool
- **`excel_to_image.py`** - Image generation utilities
- **`compdf_api.py`** - ComPDF API integration for Excel→PDF conversion
- **`templates/`** - HTML templates for web interface
- **`temp_uploads/`** - Temporary file storage (auto-created)
- **`gunicorn.conf.py`** - Production server configuration
- **`render.yaml`** - Render.com deployment configuration

## Configuration & Environment Variables

### Required for Image Generation
```bash
COMPDF_PUBLIC_KEY=your_compdf_public_key
COMPDF_SECRET_KEY=your_compdf_secret_key
```

### Optional
```bash
PORT=8000  # Server port (default: 8000 for web_server.py, 5000 for run.py)
FLASK_ENV=production  # Disables debug mode
PYTHON_VERSION=3.9.19  # For Render deployment
```

## Dependencies & System Requirements

### Python Packages (requirements.txt)
- **Flask 2.3.3** - Web framework
- **pdfplumber 0.9.0** - Primary PDF text extraction
- **PyPDF2 3.0.1** - Fallback PDF processing
- **openpyxl 3.1.2** - Excel file manipulation
- **pytesseract** - OCR for image-based PDFs
- **pdf2image** - PDF to image conversion
- **Pillow** - Image processing
- **pandas** - Data manipulation
- **Gunicorn** - Production WSGI server

### System Dependencies
- **poppler-utils** - PDF processing (`pdftotext` command)
- **tesseract-ocr** - OCR engine for image processing
- **ghostscript** - PDF manipulation support

## Common Development Patterns

### PDF Processing Strategy
The system uses a multi-layered approach for robust PDF text extraction:
1. **pdfplumber with cropping** - Primary method, crops to first column for accuracy
2. **pdftotext fallback** - System command when pdfplumber fails
3. **OCR processing** - For image-based PDFs using pytesseract
4. **Regex filtering** - Removes false positives (dates, booking codes)

### Room Number Validation
```python
# Valid room patterns: 3-4 digits, excludes years and common false positives
room_pattern = r'\b(\d{3,4})\b'
# Excludes: 19xx, 20xx (years), 2500-2600 (date ranges)
```

### Excel Template Integration
The system preserves the existing template structure and only adds "X" marks:
- Scans for "Room" headers to find column sections
- Maps OD, DO, ARR columns relative to Room column
- Updates date fields automatically based on schedule date

### Error Handling Philosophy
- **Graceful degradation** - Excel generation continues even if image creation fails
- **Multiple fallbacks** - Several PDF processing methods for robustness  
- **User-friendly errors** - Vietnamese/English bilingual error messages
- **File cleanup** - Automatic removal of temporary files

## Deployment Notes

### Render.com (render.yaml)
- Uses Python 3.9.19 runtime
- Auto-scaling: 1-3 instances
- Health check on root path
- Port determined by environment variable

### Docker (Dockerfile)
- Based on python:3.9-slim
- Includes system dependencies (poppler, tesseract, ghostscript)
- Exposes port 8000
- Health check with curl

## Testing Strategy

### Manual Testing Files
Place test PDFs in root directory:
- `arr14.08.25 (1).PDF` - Sample arrivals file
- `dep14.08.25 (1).PDF` - Sample departures file  
- `GIH01103 Guests in House by Room (2).PDF` - Sample guests in house file

### Web Interface Testing
1. Navigate to `http://localhost:8000`
2. Upload 3 PDF files with schedule date
3. Verify Excel and image generation
4. Test manual editing workflow

## Performance Considerations

- **File size limits**: 16MB max upload per file
- **Processing time**: ~30-60 seconds for full workflow including image generation
- **Memory usage**: Optimized for single worker deployment (Render free tier)
- **Concurrent requests**: Limited to 1 worker in production config

## Security Notes

- **File validation**: Only accepts PDF and image files
- **Temporary storage**: Files automatically cleaned up after processing
- **API keys**: ComPDF credentials stored as environment variables
- **Path security**: Uses secure_filename() for uploaded files
