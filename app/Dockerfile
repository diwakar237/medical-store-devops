FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ARG APP_VERSION=v1
ENV APP_VERSION=${APP_VERSION}
EXPOSE 5000
CMD ["sh","-c","python -c 'from app import initialize_database; initialize_database()' && gunicorn --bind 0.0.0.0:5000 --workers 2 app:app"]
