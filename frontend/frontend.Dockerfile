# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create logs directory and set permissions
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "web_app.py", "--server.address", "0.0.0.0"] 