# Application Overview

## What IntelliWealth Is

IntelliWealth is a wealth management dashboard for managing investment portfolios and understanding portfolio risk, allocation, and history.

It is built as a microservices application so each major business capability can evolve independently:

- Frontend user experience
- Portfolio and identity management
- Market intelligence
- AI-powered explanations
- Observability

## What IntelliWealth Is Not

IntelliWealth is not a trading platform.

It does not:

- Buy or sell securities.
- Connect to a brokerage account.
- Execute market orders.
- Provide financial advice.

The application is focused on portfolio visibility and explanation.

## Main Users

### Investor

An investor can:

- Sign up.
- Log in.
- Create a portfolio.
- Add assets.
- View dashboard metrics.
- Review allocation.
- Record portfolio history snapshots.
- Update their profile.

### Admin

An admin can:

- Log in.
- View all users.
- Create users.
- Edit user profile fields.
- Change user role.
- Activate or deactivate accounts.

## Current Real Data Flows

The app now uses backend APIs and PostgreSQL for the main workflows:

```text
Sign up
Frontend -> Portfolio Service -> PostgreSQL customers table

Login
Frontend -> Portfolio Service -> PostgreSQL customers table -> JWT token

Create portfolio
Frontend -> Portfolio Service -> PostgreSQL portfolios table

Add asset
Frontend -> Portfolio Service -> PostgreSQL assets table

Dashboard
Frontend -> Portfolio Service -> PostgreSQL portfolios/assets tables

Allocation
Frontend -> Portfolio Service -> saved assets

History
Frontend -> Portfolio Service -> PostgreSQL portfolio_history table

Admin
Frontend -> Portfolio Service -> PostgreSQL customers table
```

## Service Responsibilities

### Frontend

Location:

```text
frontend/
```

Responsibilities:

- User interface
- Signup and login pages
- Dashboard
- Portfolio management
- Asset allocation
- History
- Profile
- Admin user management

Technology:

- React
- TypeScript
- Tailwind CSS
- Recharts
- Axios

### Portfolio Service

Location:

```text
portfolio-service/
```

Responsibilities:

- Authentication
- JWT token generation
- User registration
- Customer management
- Portfolio CRUD
- Asset CRUD
- Allocation calculation
- Portfolio history snapshots

Technology:

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT

### Market Service

Location:

```text
market-service/
```

Responsibilities:

- Market data scaffolding
- Risk metric scaffolding
- Redis-backed caching

Technology:

- FastAPI
- SQLAlchemy
- Redis

### AI Insight Service

Location:

```text
ai-insight-service/
```

Responsibilities:

- Portfolio explanation
- Risk summary narration
- Scenario analysis
- Mock provider for local development
- Future Bedrock provider support

Technology:

- FastAPI
- Provider abstraction
- Optional AWS Bedrock integration

## Database Overview

The core PostgreSQL-backed entities are:

- `customers`
- `portfolios`
- `assets`
- `transactions`
- `portfolio_history`

The user account is stored in `customers`.

The portfolio belongs to a customer.

Assets belong to a portfolio.

History snapshots store point-in-time portfolio values.

## Local Demo Credentials

The seed script creates an admin user:

```text
Email: admin@intelliwealth.io
Password: admin123
```

Normal users should use the signup form.
