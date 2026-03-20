FROM python:3.11-slim

# Install ffmpeg and clean up apt cache to keep image small
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure uploads directory exists
RUN mkdir -p uploads

# Define the port environment variable with a fallback for local testing
ENV PORT=${PORT:-5001}
EXPOSE $PORT

# Start the application using Gunicorn with an extended timeout 
# (helpful for processing larger transcription files)
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 app:app
