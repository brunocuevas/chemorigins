# Start with Python 3.12 base image
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Pull uv from its official image so we can install the exact versions
# locked in `uv.lock` (pip alone would resolve `pyproject.toml`'s
# >= constraints, which drifts from what we test locally).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create and set working directory
WORKDIR /code

# System build/runtime dependencies (RDKit's wheel needs the X libs).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        git \
        libxrender1 \
        libxext-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first to leverage Docker layer caching.
COPY pyproject.toml uv.lock README.md ./

# Install only the locked third-party dependencies (skip our own project for now).
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code.
COPY app/ ./app/
COPY prebchemdb/ ./prebchemdb/
COPY scripts/ ./scripts/
COPY src/ ./src/
COPY test/ ./test/

# Now install our project itself against the already-locked deps.
RUN uv sync --frozen --no-dev

# Make the uv-managed venv the default Python for subsequent layers / CMD.
ENV PATH="/code/.venv/bin:${PATH}"

# Create directory for the image buffer and use an absolute path so it
# doesn't depend on the worker's current working directory.
RUN mkdir -p /code/app/static
ENV PREBCHEMDB_IMAGE_BUFFER=/code/app/static/

# Expose the port the app runs on.
EXPOSE 8000
WORKDIR /code/app

# Command to run the application. Timeout bumped so heavy /search/
# requests (many RDKit image renders on a cold cache) aren't SIGKILL'd
# by the default 30s worker timeout.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "-m", "007", "wsgi:app"]
