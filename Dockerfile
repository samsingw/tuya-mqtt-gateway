# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    TZ=UTC \
    PYTHONPATH=/app
# Create application directory
WORKDIR /app

# Copy application code
COPY tuya_mqtt_gw.py mqtt_handler.py api_client.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python", "tuya_mqtt_gw.py"]

