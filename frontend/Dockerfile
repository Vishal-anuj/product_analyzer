# === Frontend Dockerfile ===
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy rest of frontend
COPY frontend/ .

# Expose Next.js dev port
EXPOSE 3000

# Set environment variable for Next.js
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Start Next.js in dev mode with proper host binding
CMD ["sh", "-c", "npm run dev -- -H 0.0.0.0"]
