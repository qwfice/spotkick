#!/bin/bash
# SpotKick Deployment Script
# Run this on any server with Docker installed

echo "🚀 Deploying SpotKick..."

# Pull latest (if using git)
# git pull origin main

# Build and start
docker-compose down
docker-compose up --build -d

echo "✅ SpotKick is live at http://$(curl -s ifconfig.me):8000"
echo "📊 API docs: http://$(curl -s ifconfig.me):8000/docs"
