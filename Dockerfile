# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY .env /app

# Install any needed packages
RUN apt-get update \
    && apt-get install -y chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -r requirements.txt

# and install playwright browsers
RUN playwright install

# as well as an x-server to render browser head
RUN apt-get install -y xvfb

# Run the script
# CMD ["python", "ingest/linkedin.py"]