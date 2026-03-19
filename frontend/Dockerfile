FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev"]
