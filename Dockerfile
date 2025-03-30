# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Copy Firebase credentials (ensure it's included in .dockerignore for security)
COPY firebase_credentials.json /app/firebase_credentials.json

# Set environment variable for Firebase credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase_credentials.json

# Expose the application port
EXPOSE 5000

# Run the Flask application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
