import './BudgetProgress.css';

function BudgetProgress({ budgets }) {
  const getStatusClass = (spent, limit) => {
    const percentage = (spent / limit) * 100;
    if (percentage >= 100) return 'over-budget';
    if (percentage >= 80) return 'near-limit';
    return 'on-track';
  };

  return (
    <div className="budget-status-card">
      <div className="card-title-section">
        <h3>Budget Status</h3>
        <p className="card-subtitle">Monthly budget progress</p>
      </div>

      <div className="budget-list">
        {budgets.map((budget, index) => {
          const percentage = (budget.spent / budget.limit) * 100;
          const remaining = budget.limit - budget.spent;
          const statusClass = getStatusClass(budget.spent, budget.limit);

          return (
            <div key={index} className="budget-item">
              <div className="budget-header">
                <span className="budget-category">{budget.category}</span>
                <span className={`budget-status ${statusClass}`}>
                  {percentage >= 100 ? 'Over limit!' : `$${Math.abs(remaining).toFixed(0)} left`}
                </span>
              </div>

              <div className="budget-bar-container">
                <div
                  className={`budget-bar ${statusClass}`}
                  style={{
                    width: `${Math.min(percentage, 100)}%`,
                    backgroundColor: budget.color
                  }}
                />
                {percentage > 100 && (
                  <div
                    className="budget-bar-overflow"
                    style={{
                      width: `${percentage - 100}%`,
                      backgroundColor: '#FF4757'
                    }}
                  />
                )}
              </div>

              <div className="budget-amounts">
                <span className="amount-spent">${budget.spent.toLocaleString()}</span>
                <span className="amount-limit">of ${budget.limit.toLocaleString()}</span>
              </div>
            </div>
          );
        })}
      </div>

      <button className="btn-view-all">View All Budgets →</button>
    </div>
  );
}

export default BudgetProgress;
