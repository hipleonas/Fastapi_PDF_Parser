# Use Python 3.11 image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Set ENV so Nixpacks doesn't break
ENV NIXPACKS_PATH=/opt/venv/bin:${NIXPACKS_PATH:-}

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run your app (replace this line with your app's start command)
CMD ["python3", "main.py"]
