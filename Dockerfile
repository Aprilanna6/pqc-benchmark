# -------------------------------
# Base Image
# Use Python 3.12 slim version
# -------------------------------
FROM python:3.12-slim

# -------------------------------
# Set Working Directory
# All commands will run in /app inside the container
# -------------------------------
WORKDIR /app

# -------------------------------
# Install system dependencies
# Needed for building some packages (e.g., pqcrypto, matplotlib)
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Upgrade pip to a fixed version
# -------------------------------
RUN python -m pip install --upgrade pip==25.3

# -------------------------------
# Copy Python dependencies file
# -------------------------------
COPY requirements.txt .

# -------------------------------
# Install Python dependencies
# --no-cache-dir avoids caching to keep image small
# -------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy the rest of the project into the container
# -------------------------------
COPY . .

# -------------------------------
# Set default environment variable
# This can be overridden at runtime with -e PROFILE=Mobile/Laptop/Server
# -------------------------------
ENV PROFILE=Mobile

# -------------------------------
# Default command to run when container starts
# Runs the benchmark script
# -------------------------------
CMD ["python", "benchmark_kem.py"]

