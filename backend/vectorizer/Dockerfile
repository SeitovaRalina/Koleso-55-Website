FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /data/chroma \
    && chown -R app:app /app /data/chroma

USER app

CMD ["celery", "worker", "-A", "celery_app", "--loglevel=info"]
