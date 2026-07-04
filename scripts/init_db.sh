#!/bin/bash
set -e

echo "Creating database if not exists..."
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'refurbhub'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE refurbhub"

echo "Running migrations..."
cd "$(dirname "$0")/../backend"
alembic upgrade head

echo "Seeding stores..."
python scripts/seed_stores.py

echo "Database initialized successfully!"
