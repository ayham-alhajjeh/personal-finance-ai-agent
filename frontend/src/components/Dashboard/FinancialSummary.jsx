import './FinancialSummary.css';

function FinancialSummary({ data }) {
  const cards = [
    {
      title: 'Net Cash Flow',
      value: data.netCashFlow,
      trend: '+12.5%',
      trendUp: true,
      icon: '💰'
    },
    {
      title: 'Total Income',
      value: data.totalIncome,
      trend: '+5.2%',
      trendUp: true,
      icon: '📈'
    },
    {
      title: 'Total Expenses',
      value: data.totalExpenses,
      trend: '-8.3%',
      trendUp: true,
      icon: '💳'
    },
    {
      title: 'Budget Remaining',
      value: data.budgetRemaining,
      trend: '68% used',
      trendUp: false,
      icon: '🎯'
    },
    {
      title: 'Savings Progress',
      value: `${data.savingsProgress}%`,
      trend: 'Goal: $5,000',
      trendUp: true,
      icon: '🏆',
      isPercentage: true
    }
  ];

  const formatCurrency = (value) => {
    if (typeof value === 'string') return value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(Math.abs(value));
  };

  return (
    <div className="financial-summary">
      {cards.map((card, index) => (
        <div key={index} className="summary-card">
          <div className="card-header">
            <span className="card-icon">{card.icon}</span>
            <span className="card-title">{card.title}</span>
          </div>
          <div className="card-value">
            {card.isPercentage ? card.value : formatCurrency(card.value)}
          </div>
          <div className={`card-trend ${card.trendUp ? 'trend-up' : 'trend-down'}`}>
            <span className="trend-indicator">{card.trendUp ? '↑' : '↓'}</span>
            <span className="trend-text">{card.trend}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default FinancialSummary;
