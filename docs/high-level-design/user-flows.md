## Key User Flows

### 1. View Dashboard
1. User opens the dashboard page in the browser.
2. Frontend calls `GET /summary` to fetch aggregate data.
3. Frontend calls `GET /transactions` (maybe limited to recent N).
4. Backend reads from `transactions`, `categories`, `budgets`.
5. Frontend renders charts, totals, and recent transactions.

### 2. Add a Transaction
1. User fills a “New Transaction” form on the UI.
2. Frontend sends form data to `POST /transactions`.
3. Backend validates data and inserts a row into `transactions`.
4. Backend returns created transaction; frontend updates the list.

### 3. Edit a Transaction
1. User edits fields on the UI.
2. Frontend sends form data to `PUT /transactions/{id}`.
3. Backend validates data and edits fields of the row in `transactions`.
4. Backend returns updated transaction; frontend updates the fields.

### 4. Remove a transaction
1. User clicks delete on the UI -> confirm delete.
2. Frontend sends delete to `DELETE /transactions/{id}`.
3. Backend deletes transaction row from `transactions`.
4. Backend returns confirmation; frontend removes it from the list.

### 4. Set or Edit Budget
1. User opens Budgets page.
2. frontend calls `GET /budgets` and `GET /categories` to show both budgets + categories.
3. User creates or edits a budget.
4. Frontend sends data to `POST /budgets` (create) or `PUT /budgets{id}` (update).
5. Backend updates `budgets` + `budgets_categories`.
6. Dashboard and summary views now reflect new budget info (e.g., `/summary` uses it).

### 5. Get AI Insights
1. User clicks “Generate Insights” on dashboard.
2. Frontend calls `POST /ai/insights` (optionally with filters, e.g. date range).
3. Backend fetches relevant transactions and budget data.
4. Backend calls AI provider (LLM) and stores result in `ai_insights`.
5. Backend returns insight text to frontend; frontend displays it.

### 6. View AI Insights History
1. User opens "Insights" page.
2. Frontend calls `GET /ai/insights` (list for current user).
3. Backend reads from `/ai/insights`.
4. Frontend displays a list/timeline of past insight history.