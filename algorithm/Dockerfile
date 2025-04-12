# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code into container
COPY . .

# Set environment variables (can be overridden with .env or Docker CLI)
ENV PYTHONUNBUFFERED=1

# Run the main app
CMD ["python", "main.py"]
