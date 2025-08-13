#!/usr/bin/env python3
"""
Housekeeping Report Generator
Web application to process hotel PDFs and generate Excel reports
"""

from app import app
import os

if __name__ == '__main__':
    print("="*50)
    print("🏨 Housekeeping Report Generator")
    print("="*50)
    print()
    print("Starting Flask web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print()
    print("Files in current directory:")
    files = os.listdir('.')
    for file in sorted(files):
        if file.endswith('.PDF') or file.endswith('.xlsx'):
            print(f"  ✅ {file}")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
