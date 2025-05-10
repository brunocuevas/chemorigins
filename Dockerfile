# Start with Python 3.12 base image
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set working directory
WORKDIR /code

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Install build essentials and python dev tools needed for certain dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev

RUN apt-get update && apt-get install -y libxrender1 libxext-dev git && rm -rf /var/lib/apt/lists/*

 
# Copy the rest of the application code
COPY app/ ./app/
COPY prebchemdb/ ./prebchemdb/
COPY scripts/ ./scripts/
COPY src/ ./src/
COPY test/ ./test/

# Install Python package installer (pip) and dependencies
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir .


# Create directory for image buffer
# RUN mkdir -p /data/image-buffer
ENV PREBCHEMDB_IMAGE_BUFFER=static/



# Expose the port the app runs on
EXPOSE 8000
WORKDIR app/
# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "-m", "007", "wsgi:app"]