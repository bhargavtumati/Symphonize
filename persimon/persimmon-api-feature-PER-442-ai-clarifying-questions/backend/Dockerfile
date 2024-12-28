FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /code

# Install system dependencies, including Java
RUN apt update && \
    apt install -y curl libpq-dev gcc openjdk-17-jdk && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

# Copy code to the container
COPY ./app /code
COPY .env /

# Copy poetry.lock* in case it doesn't exist in the repo
COPY app/pyproject.toml app/poetry.lock* /code/
RUN poetry lock --no-update

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ \"$INSTALL_DEV\" == 'true' ]; then poetry install --no-root; else poetry install --no-root --only main; fi"

# Set the Python path
ENV PYTHONPATH=/code

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["/bin/sh", "-c", "uvicorn app.main:app --reload --workers 3 --host 0.0.0.0 --port 8000"]