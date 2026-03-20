#!/usr/bin/env bash
# AVAS Quick Start Script
# Run this once to set up the project for first launch

set -e

echo "🚀 AVAS — Infrastructure Inspection Intelligence Platform"
echo "========================================================="

# Check requirements
if ! command -v docker &>/dev/null; then
  echo "❌ Docker not found. Please install Docker first."
  exit 1
fi
if ! command -v docker &>/dev/null || ! docker compose version &>/dev/null; then
  echo "❌ Docker Compose not found."
  exit 1
fi

# Create .env from template if not exists
if [ ! -f .env ]; then
  echo "📋 Creating .env from template..."
  cp .env.example .env
  echo ""
  echo "⚠️  IMPORTANT: Edit .env and set all passwords before running in production!"
  echo "    nano .env"
  echo ""
fi

# Generate secrets if placeholder values detected
if grep -q "CHANGE_ME" .env; then
  echo "🔑 Generating secret keys..."
  SECRET_KEY=$(openssl rand -hex 32)
  JWT_KEY=$(openssl rand -hex 64)
  POSTGRES_PW=$(openssl rand -hex 16)
  REDIS_PW=$(openssl rand -hex 16)
  MINIO_PW=$(openssl rand -hex 16)

  sed -i.bak "s/CHANGE_ME_USE_openssl_rand_-hex_32/$SECRET_KEY/" .env
  sed -i.bak "s/CHANGE_ME_USE_openssl_rand_-hex_64/$JWT_KEY/" .env
  sed -i.bak "s/CHANGE_ME_strong_password/$POSTGRES_PW/g" .env
  sed -i.bak "s/CHANGE_ME_redis_password/$REDIS_PW/g" .env
  sed -i.bak "s/CHANGE_ME_minio_password/$MINIO_PW/g" .env
  sed -i.bak "s/CHANGE_ME_minio_user/avas_minio_user/g" .env
  rm -f .env.bak
  echo "✅ Secrets generated"
fi

echo ""
echo "🐳 Building and starting AVAS services..."
docker compose up -d --build

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 15

echo ""
echo "✅ AVAS is running!"
echo ""
echo "  Frontend:   http://localhost:3000"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost:8000/docs  (dev only)"
echo "  MinIO UI:   http://localhost:9001"
echo ""
echo "  Logs: docker compose logs -f"
echo "  Stop: docker compose down"
echo ""
