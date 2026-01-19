import { useState } from 'react';
import './TransactionList.css';

function TransactionList({ transactions, loading }) {
  const [filter, setFilter] = useState('all');

  const filteredTransactions = transactions.filter(transaction => {
    if (filter === 'all') return true;
    if (filter === 'income') return transaction.amount > 0;
    if (filter === 'expense') return transaction.amount < 0;
    return true;
  });

  return (
    <div className="transaction-list-card">
      <div className="transactions-header">
        <div className="header-title">
          <h3>Recent Transactions</h3>
          <p className="card-subtitle">{transactions.length} transactions this month</p>
        </div>
        <div className="header-actions">
          <div className="filter-chips">
            <button
              className={`filter-chip ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={`filter-chip ${filter === 'income' ? 'active' : ''}`}
              onClick={() => setFilter('income')}
            >
              Income
            </button>
            <button
              className={`filter-chip ${filter === 'expense' ? 'active' : ''}`}
              onClick={() => setFilter('expense')}
            >
              Expenses
            </button>
          </div>
          <button className="btn-view-all">View All →</button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading transactions...</p>
        </div>
      ) : filteredTransactions.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📊</span>
          <h4>No transactions yet</h4>
          <p>Add your first transaction to get started</p>
          <button className="btn-primary">+ Add Transaction</button>
        </div>
      ) : (
        <div className="transactions-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Source</th>
                <th className="amount-col">Amount</th>
                <th className="actions-col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map(transaction => (
                <tr key={transaction.id}>
                  <td className="date-cell">
                    {new Date(transaction.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric'
                    })}
                  </td>
                  <td className="description-cell">
                    <div className="transaction-description">
                      {transaction.description}
                    </div>
                  </td>
                  <td className="category-cell">
                    <span className="category-badge">{transaction.category}</span>
                  </td>
                  <td className="source-cell">{transaction.source}</td>
                  <td className={`amount-cell ${transaction.amount > 0 ? 'income' : 'expense'}`}>
                    {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                  </td>
                  <td className="actions-cell">
                    <button className="icon-btn" title="Edit">✏️</button>
                    <button className="icon-btn" title="Delete">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default TransactionList;
