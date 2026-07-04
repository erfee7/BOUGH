FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Install dependencies first — this layer is cached unless pyproject.toml/uv.lock change
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy application source code
COPY app/ ./app/

# Run the API server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]