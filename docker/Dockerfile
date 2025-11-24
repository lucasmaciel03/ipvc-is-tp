FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  postgresql-client \
  libpq-dev \
  default-libmysqlclient-dev \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
  pip install -r requirements.txt

# Copy project
COPY . .

# Make scripts executable
RUN chmod +x backend/manage.py backend/manager.py

# Expose ports
EXPOSE 8000 50051

# Default command
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
