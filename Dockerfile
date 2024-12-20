# Base Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    TZ=UTC

# Create and set working directory
WORKDIR /app

# Copy application code to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Define entrypoint command
CMD ["python", "tuya_mqtt_gw.py"]

