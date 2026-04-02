#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting taskiq worker..."
exec taskiq worker src.tasks.worker:broker
