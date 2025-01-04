# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variable for MongoDB connection
ENV MONGODB_URI=mongodb://mongo:27017/extracted_laptop_data

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]