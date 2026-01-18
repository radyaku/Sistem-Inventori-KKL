# Gunakan Python versi stabil
FROM python:3.12-slim

# Set environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies sistem
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy semua source code
COPY . /app/

# Expose port Django
EXPOSE 8000

# Jalankan pakai gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "asset_management.wsgi:application"]
