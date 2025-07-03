FROM python:3.11-slim

# Install system packages needed for some Python packages
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install Python dependencies (including gunicorn)
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
