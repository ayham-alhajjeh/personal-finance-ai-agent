import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FinancialSummary from './FinancialSummary';
import SpendingChart from '../Charts/SpendingChart';
import BudgetProgress from '../Budget/BudgetProgress';
import TransactionList from '../Transaction/TransactionList';
import AIInsights from '../AI/AIInsights';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState('this-month');
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for now - replace with actual API calls
  const financialData = {
    totalIncome: 5420.00,
    totalExpenses: 3280.50,
    netCashFlow: 2139.50,
    budgetRemaining: 1219.50,
    savingsProgress: 42
  };

  const categorySpending = [
    { category: 'Food & Dining', amount: 840, color: '#FF6B6B' },
    { category: 'Transportation', amount: 520, color: '#4ECDC4' },
    { category: 'Entertainment', amount: 380, color: '#FFE66D' },
    { category: 'Shopping', amount: 720, color: '#95E1D3' },
    { category: 'Bills', amount: 820, color: '#A8E6CF' }
  ];

  const budgets = [
    { category: 'Food & Dining', spent: 840, limit: 900, color: '#FF6B6B' },
    { category: 'Transportation', spent: 520, limit: 600, color: '#4ECDC4' },
    { category: 'Entertainment', spent: 380, limit: 300, color: '#FFE66D' },
    { category: 'Shopping', spent: 720, limit: 800, color: '#95E1D3' }
  ];

  const recentTransactions = [
    { id: 1, date: '2024-01-15', description: 'Whole Foods Market', category: 'Food & Dining', amount: -87.43, source: 'Chase Credit' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', category: 'Income', amount: 5420.00, source: 'Direct Deposit' },
    { id: 3, date: '2024-01-13', description: 'Netflix Subscription', category: 'Entertainment', amount: -15.99, source: 'Chase Credit' },
    { id: 4, date: '2024-01-12', description: 'Uber Ride', category: 'Transportation', amount: -24.50, source: 'Debit Card' },
    { id: 5, date: '2024-01-11', description: 'Amazon Purchase', category: 'Shopping', amount: -156.78, source: 'Chase Credit' }
  ];

  const insights = [
    "Food spending is up 18% vs last month.",
    "You're on track for Rent budget, but Entertainment is over limit.",
    "Consider setting a weekly cap of $75 for dining out.",
    "You've saved $342 more than last month. Great progress!"
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTransactions(recentTransactions);
      setLoading(false);
    }, 500);
  }, [dateRange]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    navigate('/login', { replace: true });
  };

  const handleAddTransaction = () => {
    // TODO: Navigate to add transaction page or open modal
    console.log('Add transaction clicked');
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>Dashboard</h1>
          <p className="subtitle">Financial overview at a glance</p>
        </div>
        <div className="header-right">
          <select
            className="date-range-selector"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="this-month">This Month</option>
            <option value="last-30">Last 30 Days</option>
            <option value="last-60">Last 60 Days</option>
            <option value="custom">Custom Range</option>
          </select>
          <button className="btn-primary" onClick={handleAddTransaction}>
            + Add Transaction
          </button>
          <button className="btn-logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Row 1: Financial Summary */}
        <section className="section-summary">
          <FinancialSummary data={financialData} />
        </section>

        {/* Row 2: Visuals */}
        <section className="section-visuals">
          <div className="visual-left">
            <SpendingChart data={categorySpending} />
          </div>
          <div className="visual-right">
            <BudgetProgress budgets={budgets} />
          </div>
        </section>

        {/* Row 3: Recent Transactions */}
        <section className="section-transactions">
          <TransactionList
            transactions={transactions}
            loading={loading}
          />
        </section>

        {/* Row 4: AI Insights */}
        <section className="section-insights">
          <AIInsights insights={insights} />
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
