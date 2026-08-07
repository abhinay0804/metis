#!/bin/bash
# Script to safely rebuild Metis Docker images to save space

echo "🛑 Stopping all running Metis Docker containers..."
docker-compose down

echo "🧹 Removing old Metis images to save space..."
docker rmi metis_frontend metis_backend -f 2>/dev/null

echo "🏗️ Rebuilding Metis Docker images..."
docker-compose build --no-cache

echo "🚀 Starting all Metis services..."
docker-compose up -d

echo "✅ System successfully updated and started!"
