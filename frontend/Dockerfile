FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm && pnpm install

# Copy source code
COPY . .

EXPOSE 3000

# Build for production and serve
RUN pnpm run build
CMD ["pnpm", "run", "preview"]