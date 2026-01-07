import React from 'react';
import { expenseAPI } from '../services/api';

const ExpenseList = ({ expenses, onExpenseDeleted }) => {
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      try {
        await expenseAPI.delete(id);
        if (onExpenseDeleted) onExpenseDeleted();
      } catch (error) {
        console.error('Error deleting expense:', error);
        alert('Failed to delete transaction');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Transactions</h2>

      {expenses.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No transactions yet. Add your first transaction to get started!</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-2 text-sm font-semibold text-gray-600">Date</th>
                <th className="text-left py-3 px-2 text-sm font-semibold text-gray-600">Category</th>
                <th className="text-left py-3 px-2 text-sm font-semibold text-gray-600">Description</th>
                <th className="text-right py-3 px-2 text-sm font-semibold text-gray-600">Amount</th>
                <th className="text-center py-3 px-2 text-sm font-semibold text-gray-600">Action</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-2 text-sm text-gray-700">{formatDate(expense.date)}</td>
                  <td className="py-3 px-2 text-sm text-gray-700">{expense.category}</td>
                  <td className="py-3 px-2 text-sm text-gray-700">{expense.description || '-'}</td>
                  <td className={`py-3 px-2 text-sm text-right font-semibold ${
                    expense.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {expense.transaction_type === 'income' ? '+' : '-'}${expense.amount.toFixed(2)}
                  </td>
                  <td className="py-3 px-2 text-center">
                    <button
                      onClick={() => handleDelete(expense.id)}
                      className="text-red-500 hover:text-red-700 text-sm font-semibold"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ExpenseList;
