import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { expenseAPI, analyticsAPI, authAPI } from '../services/api';
import ExpenseForm from '../components/ExpenseForm';
import ExpenseList from '../components/ExpenseList';
import SummaryCards from '../components/SummaryCards';
import ChartsSection from '../components/ChartsSection';

const Dashboard = () => {
  const { user, logout, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [user, authLoading, navigate]);

  const fetchData = async () => {
    try {
      const [expensesRes, summaryRes] = await Promise.all([
        expenseAPI.getAll(),
        expenseAPI.getSummary(),
      ]);

      setExpenses(expensesRes.data.expenses);
      setSummary(summaryRes.data);

      if (expensesRes.data.expenses.length >= 10) {
        const [predictionsRes, trendsRes] = await Promise.all([
          analyticsAPI.getPredictions(30).catch(() => null),
          analyticsAPI.getTrends('monthly').catch(() => null),
        ]);

        if (predictionsRes) setPredictions(predictionsRes.data);
        if (trendsRes) setTrends(trendsRes.data.trends);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleExpenseAdded = () => {
    fetchData();
  };

  const handleExpenseDeleted = () => {
    fetchData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-800">Finance Tracker</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                Welcome, {user?.username} ({user?.role})
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {summary && <SummaryCards summary={summary} predictions={predictions} />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <div className="lg:col-span-1">
            <ExpenseForm onExpenseAdded={handleExpenseAdded} />
          </div>

          <div className="lg:col-span-2">
            <ExpenseList expenses={expenses} onExpenseDeleted={handleExpenseDeleted} />
          </div>
        </div>

        {trends.length > 0 && (
          <div className="mt-8">
            <ChartsSection trends={trends} summary={summary} predictions={predictions} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
