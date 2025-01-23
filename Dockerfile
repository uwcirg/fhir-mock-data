# Use the offical Python base image
FROM python:3.11-slim

# Set enviornment variables
ENV PYTHONDONTWRITEBYTECODE=1

# Set working dir in container
WORKDIR /app

# Install build dependencies for projects using pyproject.toml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and requirements.txt first for dependency installation
COPY pyproject.toml requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Define the default command to run the application
ENTRYPOINT ["python", "timewarp/api.py"]
CMD ["main"]
