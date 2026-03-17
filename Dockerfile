FROM python:3.13-slim
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source code
COPY . .

# Create persistent data folder
RUN mkdir -p /data

# Environment variables
ENV DB_PATH="/data/btu_gacha.db"

# Run the bot
CMD ["python", "main.py"]