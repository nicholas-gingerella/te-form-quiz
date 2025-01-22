FROM node:20-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start in production mode
CMD ["npm", "start"]