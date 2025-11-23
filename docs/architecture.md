# AI Finance Dashboard — Architecture Overview

## High-Level Components
- React frontend
- FastAPI backend (Python)
- Database (PostgreSQL)
- AI Service (OpenAI / LangChain)
- Authentication service (Clerk)

## Data Flow Summary
1. User logs in
2. User uploads transactions or connects to API
3. Backend processes & stores data
4. AI agent analyzes spending patterns
5. Dashboard visualizes budgets, categories, trends