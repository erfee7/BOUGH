# BOUGH

A self-hosted personal AI agent platform. Currently in early development.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Vue 3, TypeScript
- **Database:** PostgreSQL (pgvector)
- **Infra:** Docker, Docker Compose, Nginx

## Prerequisites
- Docker & Docker Compose
- GNU Make

## Quick Start

1. Copy the environment template:
   ```bash
   cp .env.example .env
   # Add your PROVIDER_API_KEY to .env
   ```
2. Start the development environment:
   ```bash
   make dev
   ```
3. Open the app at `http://localhost:5173`