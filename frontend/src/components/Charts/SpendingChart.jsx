import './SpendingChart.css';

function SpendingChart({ data }) {
  const total = data.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="spending-chart-card">
      <div className="card-title-section">
        <h3>Spending Breakdown</h3>
        <p className="card-subtitle">By category this month</p>
      </div>

      <div className="chart-container">
        <div className="donut-chart">
          {data.map((item, index) => {
            const percentage = (item.amount / total) * 100;
            return (
              <div
                key={index}
                className="donut-segment"
                style={{
                  '--percentage': `${percentage}%`,
                  '--color': item.color,
                  '--rotation': `${data.slice(0, index).reduce((sum, i) => sum + (i.amount / total) * 360, 0)}deg`
                }}
              />
            );
          })}
          <div className="donut-center">
            <div className="donut-total">
              ${total.toLocaleString()}
              <span className="donut-label">Total Spent</span>
            </div>
          </div>
        </div>

        <div className="chart-legend">
          {data.map((item, index) => {
            const percentage = ((item.amount / total) * 100).toFixed(1);
            return (
              <div key={index} className="legend-item">
                <div
                  className="legend-color"
                  style={{ backgroundColor: item.color }}
                />
                <div className="legend-details">
                  <span className="legend-category">{item.category}</span>
                  <div className="legend-amount-row">
                    <span className="legend-amount">${item.amount.toLocaleString()}</span>
                    <span className="legend-percentage">{percentage}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default SpendingChart;
