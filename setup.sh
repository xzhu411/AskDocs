#!/bin/bash

echo "🚀 Setting up AskMyDocs..."

# Create .env file if doesn't exist
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "✓ Created backend/.env"
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose up -d

echo "⏳ Waiting for services..."
sleep 5

# Pull models
echo "📦 Pulling LLM models..."
docker compose exec -T ollama ollama pull mistral
docker compose exec -T ollama ollama pull nomic-embed-text

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access points:"
echo "  • Frontend: http://localhost:5173"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Qdrant: http://localhost:6333"
echo ""
echo "🎯 Next steps:"
echo "  1. Open http://localhost:5173"
echo "  2. Upload documents (.md, .txt, .pdf)"
echo "  3. Ask questions!"
echo ""
