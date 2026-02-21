# Use a Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files into /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["python", "run.py"]