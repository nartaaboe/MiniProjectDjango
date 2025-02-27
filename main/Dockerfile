# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (including wkhtmltopdf)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    xvfb \
    libfontconfig1 \
    libxrender1 \
    wkhtmltopdf

# Set the wkhtmltopdf path in an environment variable
ENV WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy project files
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port for Gunicorn
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]