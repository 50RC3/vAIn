# Use a Python base image
FROM python:3.11-slim

# Set environment variables to prevent .pyc files and enable unbuffered output
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Expose the port that the FastAPI (or Flask) app will run on
EXPOSE 8000

# Command to run the FastAPI application (adjust if using a different framework)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
