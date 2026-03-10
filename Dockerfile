FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first (for better layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ .

# Copy the web frontend so FastAPI can serve it as static files
# main.py looks for ../web relative to backend/, which maps to /app/web here
COPY web/ ./web/

EXPOSE 8000

# Run with uvicorn from /app (where main.py lives)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
