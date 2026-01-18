# COASV (Cooperative Accounting System View)

A comprehensive, double-entry accounting interface designed for Cooperatives. Built upon the [COASC](https://github.com/suresh466/django-coasc) (Cooperative Accounting System Core) model layer.

## 🚀 Key Features

- **Financial Management**: Complete General Journal and Transaction recording.
- **Ledgers**: Automated tracking for Assets, Liabilities, Sales, Purchases, and General Ledger.
- **Financial Statements**: Real-time generation of Balance Sheets, Income Statements, and Trial Balances.
- **Inventory System**: Integrated inventory tracking and sales transaction management.
- **Loan Management**: Robust system for managing loans, billing cycles, and payment tracking.

## 🛠️ Tech Stack

### Backend

- **Language**: Python 3.12+
- **Framework**: Django 5
- **Core Engine**: [COASC](https://github.com/suresh466/django-coasc) (Accounting Logic Layer)
- **Database**: PostgreSQL
- **Server**: Gunicorn

### Frontend

- **Styling**: Tailwind CSS v4
- **Templating**: Django Templates

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Web Server / Proxy**: Caddy
- **Package Management**: uv (Python), npm (JS/CSS)

## 📦 Getting Started

### Development Setup

To run the application locally in a development environment:

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url> && cd coasv
   ```

2. **Start with Docker Compose**:

   ```bash
   docker compose -f docker-compose-dev.yml --env-file env.dev up --build
   ```

   The application will be available at `http://localhost:8000`.

### Production Deployment

For production environments, the application is optimized to run behind a Caddy web server.

1. **Configure Environment**:
   Create a production `.env` file from the development template:

   ```bash
   cp env.dev .env
   # Edit .env with your production secure keys and database credentials
   ```

2. **Deploy**:

   ```bash
   docker compose up -d --build
   ```

3. **Web Server**:
   Ensure Caddy is configured to reverse proxy to the application container (default port 8000).

## ℹ️ About

- **COASV**: Cooperative Accounting System **View** (Frontend/Interface)
- **COASC**: Cooperative Accounting System **Core** (Logic/Backend Library)

