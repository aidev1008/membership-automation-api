#!/bin/bash
# AWS Lightsail startup script for Schmick Automation

echo "🚀 Starting Schmick Automation setup..."

# Update system
apt update && apt upgrade -y

# Install Docker
apt install -y docker.io docker-compose
systemctl start docker
systemctl enable docker

# Create app directory
mkdir -p /opt/schmick-app
cd /opt/schmick-app

# Create docker-compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  schmick-app:
    image: schmick-automation:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "80:8000"
    environment:
      - HEADLESS=true
      - HOST=0.0.0.0
      - PORT=8000
      - SCHMICK_USER=CHANGE_ME
      - SCHMICK_PASS=CHANGE_ME
      - PLAYWRIGHT_API_KEY=test-demo-key-12345
    restart: unless-stopped
EOF

# Clone repository
git clone https://github.com/aidev1008/membership-automation-api.git .

# Create simple Dockerfile
cat > Dockerfile << 'EOF'
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python -m playwright install firefox
RUN python -m playwright install-deps firefox
EXPOSE 8000
CMD ["python", "app.py"]
EOF

echo "✅ Setup completed! Please update credentials in /opt/schmick-app/docker-compose.yml"
echo "Then run: cd /opt/schmick-app && docker-compose up -d"