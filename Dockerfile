# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    portaudio19-dev \
    python3-dev \
    build-essential \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model for NER
RUN python -m spacy download en_core_web_sm

# Copy project files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/media /app/logs /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create a non-root user and switch to it
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE ${PORT:-8000}

# Run migrations and start server
CMD python manage.py migrate && \
    gunicorn truthtell.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120
