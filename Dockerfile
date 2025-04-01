# Use official Python image
FROM python:3.10-slim

# Set working dir
WORKDIR /app

# Install system dependencies (for PIL/Image support)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Start the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]