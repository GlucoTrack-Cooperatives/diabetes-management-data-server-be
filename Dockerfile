# Use a slim Python 3.11 image for a small, fast container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL (needed for psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Ensure logs are sent to the console immediately (crucial for GKE logging)
ENV PYTHONUNBUFFERED=1

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]