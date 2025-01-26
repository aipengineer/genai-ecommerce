# src/genai_ecommerce_web/__main__.py
import os

import uvicorn

from .app import app

if __name__ == "__main__":
    # Default to localhost for security; allow overriding with an environment variable
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
