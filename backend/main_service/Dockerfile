FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip

# Set work directory
WORKDIR /app

# Copy requirements and install (include PyTorch index if needed)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy project
COPY . .

# Create runtime user and writable directories
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && mkdir -p media static /var/lib/celery /data/huggingface \
    && chown -R app:app /app /var/lib/celery /data/huggingface

USER app

# Expose port
EXPOSE 8000

# Default command: migrate + collectstatic + runserver
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
