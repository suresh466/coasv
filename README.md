# COASV (Cooperative Accounting System View)

A comprehensive, double-entry accounting interface designed for Cooperatives. Built upon the [COASC](https://github.com/suresh466/django-coasc) (Cooperative Accounting System Core) model layer.

## 🚀 Key Features

- **Financial Management**: Complete General Journal and Transaction recording.
- **Ledgers**: Automated tracking for Assets, Liabilities, Sales, Purchases, and General Ledger.
- **Financial Statements**: Real-time generation of Balance Sheets, Income Statements, and Trial Balances.
- **Inventory System**: Integrated inventory tracking and sales transaction management.
- **Loan Management**: Robust system for managing loans, billing cycles, and payment tracking.

## 🛠️ Tech Stack

- **Backend:** Python 3.12+, Django, [COASC](https://github.com/suresh466/django-coasc) (Core), PostgreSQL, Gunicorn
- **Frontend:** Tailwind CSS v4, Django Templates
- **Infrastructure:** Docker/Compose, Caddy, uv (Python), npm (JS/CSS)

## 📦 Getting Started

### Using docker

1. **Clone the repository**:

   ```bash
   git clone https://github.com/suresh466/coasv.git && cd coasv
   ```

2. **Start with Docker Compose**:

   ```bash
   docker compose --env-file env.dev up
   ```

The application will be available at `http://localhost:8000`
