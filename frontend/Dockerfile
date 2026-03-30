# Frontend Dockerfile — LOCAL DEVELOPMENT ONLY
# Not optimised for production use.

FROM node:20-slim

WORKDIR /app

# Copy dependency manifest and install Node packages
COPY package.json ./
RUN npm install

# Copy application source
COPY . .

# Run Next.js in development mode with hot-reload
CMD ["npm", "run", "dev"]
