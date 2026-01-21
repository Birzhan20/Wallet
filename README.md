# Mini-Wallet API

REST API for a mini-wallet system. Built with Django and PostgreSQL.

## Technology Stack
- Python 3.13
- Django 6.0
- Django REST Framework
- PostgreSQL 15
- Pytest
- Docker

## Features
- Atomic Transactions: Prevents balance errors during transfers.
- Race Condition Protection: Uses database locks to handle multiple requests at once.
- Automatic Wallets: Creates a wallet automatically when a user registers.
- Docker Support: Application and database run in containers.

## How to Run

### 1. Setup
Create a file named `.env` in the project root directory. Use these settings:
```env
SECRET_KEY=your_secret_key
POSTGRES_DB=wallet_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=wallet_db
POSTGRES_PORT=5432
```

### 2. Start Project
Run this command in your terminal:
```bash
docker-compose up --build
```
The API will be available at http://localhost:8000/

## Testing
To run tests inside the container:
```bash
docker exec -it wallet_back python -m pytest
```

## API Endpoints

### Users
- POST /wallet/register/ - Register a new user (username, email, password).

### Wallets and Transfers
- GET /wallet/wallets/ - View your current balance (requires authentication).
- POST /wallet/transfer/ - Transfer money to another user. Request body:
  ```json
  {
    "receiver_email": "user@example.com",
    "amount": "100.00"
  }
  ```

## Security Rules
- You cannot transfer money to yourself.
- You cannot transfer more money than you have.
- Database records are locked during the transfer process to prevent double spending.
