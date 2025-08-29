FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm && pnpm install

# Copy source code
COPY . .

EXPOSE 3000

# Run development server with host binding
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]