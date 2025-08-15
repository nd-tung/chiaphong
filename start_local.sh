#!/bin/bash
# Start local development server with environment variables

# Load environment variables from .env.local (for local development with real credentials)
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env.local"
elif [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
    if [[ "$COMPDF_PUBLIC_KEY" == *"your_"* ]] || [[ "$COMPDF_SECRET_KEY" == *"your_"* ]]; then
        echo "⚠️  Using template credentials. Create .env.local with real credentials for full functionality."
    fi
else
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please create .env.local file with your actual ComPDF API credentials"
fi

# Display loaded environment variables (masked for security)
echo "📋 Environment Configuration:"
echo "   COMPDF_PUBLIC_KEY: ${COMPDF_PUBLIC_KEY:0:20}..."
echo "   COMPDF_SECRET_KEY: ${COMPDF_SECRET_KEY:0:20}..."
echo "   FLASK_ENV: ${FLASK_ENV:-development}"
echo "   PORT: ${PORT:-8000}"

# Check if credentials are set
if [[ "$COMPDF_PUBLIC_KEY" == *"your_"* ]] || [[ "$COMPDF_SECRET_KEY" == *"your_"* ]]; then
    echo "❌ ComPDF API credentials not configured!"
    echo "   Please edit .env file with real credentials"
    exit 1
fi

echo ""
echo "🏨 Starting Hotel Room Classification System..."
echo "🌐 Server will be available at: http://localhost:${PORT:-8000}"
echo "📋 Features available:"
echo "   ✅ PDF Processing (ARR, DEP, GIH)"
echo "   ✅ Excel Template Generation"  
echo "   ✅ Image Generation (ComPDF API)"
echo "   ✅ Manual Editing Interface"
echo ""
echo "Press Ctrl+C to stop the server"
echo "─────────────────────────────────────────"

# Start the Flask server
python3 web_server.py
