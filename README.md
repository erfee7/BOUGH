# BOUGH

A self-hosted personal AI agent platform. Currently in early development.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Vue 3, TypeScript
- **Database:** PostgreSQL (pgvector)
- **Infra:** Docker, Docker Compose, Caddy

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
3. In a new terminal window, create your initial admin account:
   ```bash
   make manage create-user admin
   # (A secure password will be auto-generated and printed in the terminal)
   ```
4. Open the app at `http://localhost:5173` and log in with your new account.