# Development Stage
FROM node:23-alpine3.20 AS development

WORKDIR /app

# Install dependencies first (caching)
COPY package*.json ./
RUN npm ci --force

# Copy rest of the application
COPY . .

# Build argument for API URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]

# Production Stage
FROM node:23-alpine3.20 AS production

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --force

# Build argument for API URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy source
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start production server
CMD ["npm", "start"]