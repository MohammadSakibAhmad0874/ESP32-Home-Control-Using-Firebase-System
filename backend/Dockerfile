FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY . .

# The web/ folder is copied into backend/web/ before building
# (so COPY . . above picks it up at /app/web/)
# main.py detects this and serves it from /app/web/

EXPOSE 8000

# Run with uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
