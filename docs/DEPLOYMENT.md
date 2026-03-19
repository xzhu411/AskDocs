# AskMyDocs - Deployment Guide

## Local Development (Current Setup)

Your **docker-compose.yml** is already configured for local development with:
- FastAPI backend (port 8000)
- React frontend (port 5173)
- Qdrant vector DB (port 6333)
- Ollama LLM (port 11434)

### Start Local
```bash
cd /Users/zhuxiaoai/Projects/AskMyDocs
chmod +x setup.sh
./setup.sh
```

## Production Deployment

### Option 1: Docker Swarm (Simple, Production-Ready)

```bash
# Build images
docker build -t askmydocs-backend:v1 backend/
docker build -t askmydocs-frontend:v1 frontend/

# Push to registry (ECR, Docker Hub, etc.)
docker tag askmydocs-backend:v1 your-registry/askmydocs-backend:v1
docker push your-registry/askmydocs-backend:v1

# Deploy
docker stack deploy -c docker-compose.prod.yml askmydocs
```

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  backend:
    image: your-registry/askmydocs-backend:v1
    environment:
      - DEBUG=false
      - OLLAMA_BASE_URL=https://llm-service.com
      - QDRANT_URL=https://qdrant-cloud.com
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G
  frontend:
    image: your-registry/askmydocs-frontend:v1
    deploy:
      replicas: 2
```

### Option 2: AWS ECS/Fargate (Recommended)

1. **Create ECR Repositories**
```bash
aws ecr create-repository --repository-name askmydocs-backend
aws ecr create-repository --repository-name askmydocs-frontend
```

2. **Push Images**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

# Build and push backend
docker build -t askmydocs-backend .
docker tag askmydocs-backend:latest YOUR_ECR_URI/askmydocs-backend:latest
docker push YOUR_ECR_URI/askmydocs-backend:latest

# Same for frontend
```

3. **Create ECS Task Definition** (askmydocs-task.json)
```json
{
  "family": "askmydocs",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ECR_URI/askmydocs-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "DEBUG", "value": "false"},
        {"name": "OLLAMA_BASE_URL", "value": "https://llm-prod.com"},
        {"name": "QDRANT_URL", "value": "https://qdrant-prod.com"}
      ]
    },
    {
      "name": "frontend",
      "image": "YOUR_ECR_URI/askmydocs-frontend:latest",
      "portMappings": [{"containerPort": 5173}]
    }
  ]
}
```

4. **Deploy to ECS**
```bash
aws ecs create-service \
  --cluster askmydocs-cluster \
  --service-name askmydocs \
  --task-definition askmydocs \
  --desired-count 2
```

### Option 3: Kubernetes (Advanced)

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: askmydocs-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: askmydocs-backend
  template:
    metadata:
      labels:
        app: askmydocs-backend
    spec:
      containers:
      - name: backend
        image: your-registry/askmydocs-backend:v1
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "false"
        - name: QDRANT_URL
          value: "http://qdrant-service:6333"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: askmydocs-backend-service
spec:
  selector:
    app: askmydocs-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/
```

## Production Configuration

### Environment Variables

```env
# Security
DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=your-secret-key-here

# Services (use managed services in production)
QDRANT_URL=https://your-qdrant-cloud.com
QDRANT_API_KEY=your-secure-key
OLLAMA_BASE_URL=https://your-llm-service.com

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@db-server:5432/askmydocs

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=/data/uploads

# RAG
RETRIEVAL_K=5
RERANK_TOP_K=3

# Caching
REDIS_URL=redis://redis-server:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## Health Checks & Monitoring

### Add Health Endpoints
```python
@app.get("/health/live")
async def health_live():
    return {"status": "alive"}

@app.get("/health/ready")
async def health_ready():
    try:
        # Check database connections
        await qdrant_client.get_collections()
        return {"status": "ready"}
    except:
        return {"status": "not_ready"}, 503
```

### Monitoring Stack (Optional)
```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy AskMyDocs
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: |
          docker build -t askmydocs-backend:${{ github.sha }} backend/
          docker build -t askmydocs-frontend:${{ github.sha }} frontend/
      
      - name: Push to registry
        run: |
          docker push askmydocs-backend:${{ github.sha }}
          docker push askmydocs-frontend:${{ github.sha }}
      
      - name: Deploy to production
        run: |
          # Your deployment command
          aws ecs update-service --cluster askmydocs \
            --service askmydocs \
            --image ${{ github.sha }}
```

## Scaling Considerations

### Horizontal Scaling
- Run multiple backend instances behind load balancer
- Use Qdrant Cloud for managed vector DB
- Cache responses with Redis

### Vertical Scaling
- Increase CPU/memory limits per container
- Use faster embedding models
- Cache embeddings

### Performance Tips
1. **Batch Processing**: Process documents in batches
2. **Async Handlers**: Use async/await for I/O
3. **Caching**: Cache embeddings and reranker scores
4. **Connection Pooling**: Reuse DB connections

## Backup & Disaster Recovery

```bash
# Backup Qdrant data
docker cp qdrant:/qdrant/storage ./backup/qdrant-backup

# Backup uploaded documents
tar -czf backup/documents-$(date +%s).tar.gz backend/uploads/

# Automated backups (cron)
0 2 * * * tar -czf /backups/askmydocs-$(date +\%Y\%m\%d).tar.gz /data/askmydocs
```

## SSL/TLS Setup

### Using Let's Encrypt with Nginx
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://backend:8000;
    }
}
```

## Troubleshooting Production

```bash
# Check service health
curl https://yourdomain.com/health

# View logs
docker logs askmydocs-backend

# Monitor performance
docker stats

# Check resource usage
aws ecs describe-services --services askmydocs
```

## Cost Optimization

1. **Use Spot Instances** (save 70% on AWS)
2. **Reserved Capacity** for stable baseline
3. **Managed Services** (Qdrant Cloud, managed LLM endpoints)
4. **Auto-scaling** based on metrics
5. **CDN** for frontend (CloudFront, Cloudflare)

## Support & Resources

- Production checklist: See PRODUCTION_CHECKLIST.md
- Performance tuning: See PERFORMANCE.md
- Security hardening: See SECURITY.md
