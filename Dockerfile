# Use the official lightweight Python image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Upgrade pip and install essential system dependencies if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project codebase into the container
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Command to securely run the Streamlit application natively
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
