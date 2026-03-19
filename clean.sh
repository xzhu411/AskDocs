#!/bin/bash

echo "🧹 Cleaning up..."
docker compose down -v
rm -rf backend/uploads/*
echo "✅ Cleaned! Volumes removed."
