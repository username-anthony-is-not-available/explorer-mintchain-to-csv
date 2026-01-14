#!/bin/bash
#
# This script is used to bootstrap the project for development.
#
set -e

# Check for Docker
if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed. Please install Docker and try again." >&2
  exit 1
fi

# Check for Docker Compose
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "Error: Docker Compose is not installed. Please install Docker Compose and try again." >&2
  exit 1
fi

# Check if .env file exists, if not copy from .env.example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
fi

echo "Building Docker image..."
docker-compose build

echo "Setup complete. To run the application, use the following command:"
echo "docker-compose run --rm app --wallet YOUR_WALLET_ADDRESS"
