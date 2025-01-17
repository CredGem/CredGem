# CredGem

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/hourone-ai/CredGem/issues)

</div>

<table>
<tr>
<td width="50%">
<img src="https://github.com/user-attachments/assets/71483f4d-ed7a-4ade-8163-5fe513724952" alt="CredGem Logo" width="100%">
</td>
<td width="50%">
<img src="https://github.com/user-attachments/assets/e6676e3b-02e5-4f31-aeca-2606181f63ef" alt="CredGem Logo" width="100%">
</td>
</tr>
</table>

<div style="flex: 1;">
    <h2>Overview</h2>
    <p>CredGem is a modern credit balance management system designed for organizations to efficiently track and manage credit balances. It provides a robust REST API backend and an intuitive admin-panel application, making credit management seamless and reliable.</p>
  </div>

## Features

- 🔐 Secure credit balance tracking
- 📊 Real-time balance updates
- 🔄 Transaction history management
- 📱 Responsive web interface
- 🔌 RESTful API
- 📈 Analytics and reporting
- 🔒 Role-based access control

## 🚀 Tech Stack

### Admin Panel
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: React Query
- **Code Quality**: ESLint, Prettier
- **Package Manager**: npm
- **Testing**: Jest, React Testing Library

### Server
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Package Manager**: Poetry
- **Testing**: pytest with pytest-cov for coverage
- **Code Quality**: pylint, black, isort
- **Documentation**: OpenAPI/Swagger

### Infrastructure
- **Database**: PostgreSQL 15+
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Version Control**: Git
- **API Documentation**: ReDoc

## 🏗️ Project Structure

```
CredGem/
├── admin-panel/          # React admin interface
│   ├── src/             # Source code
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── utils/       # Utility functions
│   │   └── types/       # TypeScript type definitions
│   ├── public/          # Static assets
│   └── tests/           # Test suite
├── server/              # Python server application
│   ├── src/            # Source code
│   │   ├── api/        # API endpoints
│   │   ├── core/       # Core business logic
│   │   ├── models/     # Data models
│   │   └── utils/      # Utility functions
│   ├── tests/          # Test suite
│   └── scripts/        # Utility scripts
└── docker/             # Docker configuration
    ├── admin-panel/    # Admin Panel Docker setup
    ├── server/         # Server Docker setup
    └── nginx/          # Nginx configuration

```

## 🛠️ Setup & Installation

### Prerequisites

Before you begin, ensure you have the following installed:
- Docker Engine (20.10.0+)
- Docker Compose (2.0.0+)
- Node.js (18.x+)
- Python (3.11+)
- Poetry (1.4.0+)
- PostgreSQL (15+)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/hourone-ai/CredGem.git
cd CredGem

# Start the entire stack
docker compose up -d
```

The application will be available at:
- admin-panel: http://localhost:3000
- Server API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

#### Admin Panel Development
```bash
cd admin-panel

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

#### Server Development
```bash
cd server

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run development server
poetry run python -m uvicorn src.main:app --reload

# Run tests
poetry run pytest

# Run linting
poetry run pylint src/
```

## 🧪 Testing

We maintain a comprehensive test suite for both server and admin panel:

```bash
# Run all tests
make test

# Run admin panel tests with coverage
cd admin-panel && npm run test:coverage

# Run server tests with coverage
cd server && poetry run pytest --cov
```

## 📝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Run the tests (`make test`)
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

- [API Documentation](https://hourone-ai.github.io/CredGem/redoc)
- [User Guide](https://hourone-ai.github.io/CredGem/guide)
- [Developer Documentation](https://hourone-ai.github.io/CredGem/docs)

## 🤝 Support

- Create a [GitHub Issue](https://github.com/hourone-ai/CredGem/issues) for bug reports and feature requests
- Join our [Discord Community](https://discord.gg/CredGem) for questions and discussions

## ⭐️ Show your support

Give a ⭐️ if this project helped you!

## 🚀 API Quickstart Guide

Follow these steps to get started with CredGem:

### 1. Create a Credit Type
First, define the type of credits you'll be managing:

```bash
curl -X POST http://localhost:8000/api/v1/credit-types \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "regular",
    "description": "Standard currency credits"
  }'
```

Response:
```json
{
  "id": "credit_type_123",
  "name": "regular",
  "description": "Standard currency credits",
  "created_at": "2024-03-20T10:00:00Z"
}
```

### 2. Create a Wallet
Next, create a wallet to hold the credits:

```bash
curl -X POST http://localhost:8000/api/v1/wallets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Main Wallet",
    "context": {
      "user_id": "user_123",
      "organization": "acme_corp"
    }
  }'
```

Response:
```json
{
  "id": "wallet_123",
  "name": "User Main Wallet",
  "context": {
    "user_id": "user_123",
    "organization": "acme_corp"
  },
  "status": "active",
  "created_at": "2024-03-20T10:01:00Z"
}
```

### 3. Deposit Credits
Add credits to the wallet:

```bash
curl -X POST http://localhost:8000/api/v1/wallets/wallet_123/deposit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "deposit",
    "credit_type_id": "credit_type_123",
    "description": "Initial deposit",
    "issuer": "system",
    "payload": {
      "type": "deposit",
      "amount": 100.00
    },
    "context": {
      "source": "bank_transfer",
      "reference": "tx_789"
    }
  }'
```

Response:
```json
{
  "id": "tx_abc123",
  "type": "deposit",
  "credit_type_id": "credit_type_123",
  "description": "Initial deposit",
  "context": {
    "source": "bank_transfer",
    "reference": "tx_789"
  },
  "idempotency_key": "abc123",
  "payload": {
    "type": "deposit",
    "amount": 100.00
  },
  "created_at": "2024-03-20T10:02:00Z"
}
```

### 4. Debit Credits
Spend credits from the wallet:

```bash
curl -X POST http://localhost:8000/api/v1/wallets/wallet_123/debit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "debit",
    "credit_type_id": "credit_type_123",
    "description": "Service purchase",
    "issuer": "system",
    "payload": {
      "type": "debit",
      "amount": 50.00
    },
    "context": {
      "purpose": "service_payment",
      "service_id": "srv_456"
    }
  }'
```

Response:
```json
{
  "id": "tx_def456",
  "type": "debit",
  "credit_type_id": "credit_type_123",
  "description": "Service purchase",
  "context": {
    "purpose": "service_payment",
    "service_id": "srv_456"
  },
  "idempotency_key": "def456",
  "payload": {
    "type": "debit",
    "amount": 50.00
  },
  "created_at": "2024-03-20T10:03:00Z"
}
```

### 5. Check Wallet Status
View the final state of your wallet:

```bash
curl -X GET http://localhost:8000/api/v1/wallets/wallet_123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": "wallet_123",
  "name": "User Main Wallet",
  "context": {
    "user_id": "user_123",
    "organization": "acme_corp"
  },
  "status": "active",
  "balances": [
    {
      "credit_type_id": "credit_type_123",
      "available": 50.00,
      "held": 0.00,
      "spent": 50.00,
      "overall_spent": 50.00
    }
  ],
  "created_at": "2024-03-20T10:01:00Z",
  "updated_at": "2024-03-20T10:03:00Z"
}
```

For more advanced operations like holds, releases, and adjustments, see our [complete API documentation](https://hourone-ai.github.io/CredGem/redoc).
