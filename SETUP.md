# 🚀 Setup Guide

## Local Development

### 1. Environment Variables
Create a `.env.local` file (this file is gitignored and won't be committed):

```bash
# Copy template
cp .env.example .env.local

# Edit with your actual credentials
nano .env.local
```

Content of `.env.local`:
```bash
COMPDF_PUBLIC_KEY=your_actual_public_key_here
COMPDF_SECRET_KEY=your_actual_secret_key_here
FLASK_ENV=development
PORT=8000
```

### 2. Run Local Server
```bash
# Install dependencies
pip3 install -r requirements.txt

# Start server with auto-loaded environment variables
./start_local.sh
```

## Render Deployment

### 1. Environment Variables Setup in Render Dashboard
In your Render service settings, add these environment variables:

```
COMPDF_PUBLIC_KEY = your_actual_public_key_here
COMPDF_SECRET_KEY = your_actual_secret_key_here
FLASK_ENV = production
```

The `PORT` variable is automatically set by Render.

### 2. Deploy Process
1. Push code to your GitHub repository
2. Render will automatically:
   - Run `build.sh` to install system dependencies
   - Install Python packages from `requirements.txt`  
   - Start the server with `python web_server.py`

### 3. System Dependencies (Auto-installed)
The `build.sh` script automatically installs:
- `poppler-utils` - PDF text extraction
- `tesseract-ocr` - OCR for image processing
- `ghostscript` - PDF manipulation

## Security Notes

- ✅ `.env.local` is gitignored and contains real credentials (local only)
- ✅ `.env` contains template values (safe to commit)
- ✅ `render.yaml` does not contain hardcoded credentials
- ✅ Credentials are configured through Render's environment variables interface

## Features Available

With proper credentials configured:
- 📄 PDF Processing (ARR, DEP, GIH files)
- 📊 Excel Template Generation  
- 🖼️ Image Generation (Excel → PDF → PNG)
- ✏️ Manual Editing Interface
- 🔍 OCR Support for image files
- 💾 File Download/Preview

## Troubleshooting

### Local Development
- **Image generation fails**: Check if ComPDF API credentials are correctly set in `.env.local`
- **Server won't start**: Make sure port 8000 is not in use: `lsof -i :8000`

### Render Deployment  
- **Build fails**: Check if system dependencies are being installed correctly
- **Image generation fails**: Verify ComPDF credentials are set in Render environment variables
- **App crashes**: Check Render logs for Python/system dependency issues
