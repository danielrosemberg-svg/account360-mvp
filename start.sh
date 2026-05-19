#!/bin/bash
# Account 360 MVP — start the local server
# Double-click this file in Finder, or run: bash start.sh

cd "/Users/daniel.rosemberg/Desktop/Account 360 MVP"

# Activate virtual environment
source .venv/bin/activate

echo ""
echo "  Account 360 MVP is starting..."
echo "  Open in your browser: http://127.0.0.1:8000"
echo "  Presentation:         http://127.0.0.1:8000/presentation"
echo ""
echo "  Press Ctrl+C to stop the server."
echo ""

# Open the browser automatically after 1 second
(sleep 1 && open http://127.0.0.1:8000) &

uvicorn backend.main:app --host 127.0.0.1 --port 8000
