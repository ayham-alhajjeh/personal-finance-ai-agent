## API Overview

| Endpoint                | Method | Auth? | Description                                                  |
|-------------------------|--------|-------|--------------------------------------------------------------|
| `/health`               | GET    | No    | Simple health check to verify the backend is running.        |
| `/me`                   | GET    | Yes   | Returns the current user's profile info.                     |
| `/transactions`         | GET    | Yes   | List transactions for the current user (with filters later). |
| `/transactions`         | POST   | Yes   | Create a new transaction for the current user.               |
| `/transactions/{id}`    | PUT    | Yes   | Update an existing transaction.                              |
| `/transactions/{id}`    | DELETE | Yes   | Delete a transaction.                                        |
| `/categories`           | GET    | Yes   | List the user's categories (or global + user-defined).       |
| `/categories`           | POST   | Yes   | Create a new custom category for the user.                   |
| `/budgets`              | GET    | Yes   | List budgets for the current user.                           |
| `/budgets`              | POST   | Yes   | Create a new budget (e.g. monthly budget).                   |
| `/budgets/{id}`         | GET    | Yes   | Get details for a single budget, including per-category limits. |
| `/summary`              | GET    | Yes   | Return spending summary (totals, by category, vs budget).    |
| `/ai/insights`          | POST   | Yes   | Generate AI insights based on recent user data / filters.    |