#!/bin/bash
set -e

export DATABASE_URL="postgresql+asyncpg://ai_tagger:secret_password@postgres:5432/ai_tagger"

echo "Running migrations..."
alembic upgrade head

echo "Starting bot..."
exec python main.py
