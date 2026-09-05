import os
import sys
import uvicorn
from pathlib import Path

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting AI Teacher Backend Service on http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
