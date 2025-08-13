# Use official lightweight Node.js image
FROM node:20-alpine

# Install bash, git, and Docker CLI for completeness
RUN apk add --no-cache bash git

# Set working directory inside the container
WORKDIR /smart-contracts

# Install hardhat globally
RUN npm install -g hardhat@2.26.2