FROM python:3.11-slim

WORKDIR /app

# Installing system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Grabbing envrionemnt dependencies and installing them
COPY envDependencies.txt .
RUN pip install --no-cache-dir -r envDependencies.txt

# Copy application code
COPY app/ ./app/

# Exposing port
EXPOSE 8000

# Run the application (use "fastapi run" for production)
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
