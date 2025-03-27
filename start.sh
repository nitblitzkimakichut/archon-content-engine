#!/bin/bash

# Default port is 8000 if not set
PORT=${PORT:-8000}

# Start the application with the specified port
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 