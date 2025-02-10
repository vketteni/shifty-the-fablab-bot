# Use a lightweight Python image
FROM python:3.10-slim

WORKDIR /app

# Copy dependency definitions and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (must match the port in docker-compose.yml)
EXPOSE 8000

# Run the application with Uvicorn (for FastAPI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
