#!/bin/bash

echo "📋 Checking AskMyDocs System Status..."
echo ""

# Check Docker
echo "🐳 Docker Status:"
if command -v docker &> /dev/null; then
  echo "  ✓ Docker installed"
  if docker ps -q &> /dev/null; then
    echo "  ✓ Docker daemon running"
  else
    echo "  ✗ Docker daemon not running"
    exit 1
  fi
else
  echo "  ✗ Docker not installed"
  exit 1
fi

echo ""
echo "🔍 Service Status:"

# Check if services are running
RUNNING_CONTAINERS=$(docker compose ps -q)

if [ -z "$RUNNING_CONTAINERS" ]; then
  echo "  ⚠ No services running. Start with: ./setup.sh"
else
  echo "  ✓ Services running"
  
  # Check individual services
  echo ""
  echo "📊 Detailed Status:"
  
  # Frontend
  if docker compose exec -T frontend npm list &> /dev/null 2>&1; then
    echo "  ✓ Frontend: Ready (http://localhost:5173)"
  else
    echo "  ⏳ Frontend: Starting..."
  fi
  
  # Backend
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Backend: Ready (http://localhost:8000)"
  else
    echo "  ⏳ Backend: Starting..."
  fi
  
  # Qdrant
  if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "  ✓ Qdrant: Ready (http://localhost:6333)"
  else
    echo "  ⏳ Qdrant: Starting..."
  fi
  
  # Ollama
  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  ✓ Ollama: Ready (http://localhost:11434)"
    # Check if models are available
    MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | wc -l)
    echo "    └─ $MODELS models available"
  else
    echo "  ⏳ Ollama: Starting..."
  fi
fi

echo ""
echo "📝 Quick Links:"
echo "  • Frontend: http://localhost:5173"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Vector DB: http://localhost:6333"
echo ""
echo "💡 Useful Commands:"
echo "  ./setup.sh   - Start all services"
echo "  ./stop.sh    - Stop all services"
echo "  ./clean.sh   - Reset everything"
echo ""
