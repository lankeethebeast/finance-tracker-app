import React from 'react';

const SummaryCards = ({ summary, predictions }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-semibold">Total Income</p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              ${summary.total_income.toFixed(2)}
            </p>
          </div>
          <div className="bg-green-100 p-3 rounded-full">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-semibold">Total Expenses</p>
            <p className="text-2xl font-bold text-red-600 mt-2">
              ${summary.total_expenses.toFixed(2)}
            </p>
          </div>
          <div className="bg-red-100 p-3 rounded-full">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
            </svg>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-semibold">Balance</p>
            <p className={`text-2xl font-bold mt-2 ${summary.balance >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
              ${summary.balance.toFixed(2)}
            </p>
          </div>
          <div className={`${summary.balance >= 0 ? 'bg-blue-100' : 'bg-orange-100'} p-3 rounded-full`}>
            <svg className={`w-8 h-8 ${summary.balance >= 0 ? 'text-blue-600' : 'text-orange-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      {predictions && (
        <div className={`rounded-lg shadow-md p-6 text-white ${predictions.meets_accuracy_threshold ? 'bg-gradient-to-br from-green-500 to-emerald-600' : 'bg-gradient-to-br from-orange-500 to-red-600'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white text-sm font-semibold opacity-90">
                {predictions.days_predicted}-Day Forecast
              </p>
              <p className="text-2xl font-bold mt-2">
                ${predictions.total_predicted.toFixed(2)}
              </p>
              <p className="text-xs opacity-75 mt-1">
                Avg: ${predictions.average_per_day.toFixed(2)}/day
              </p>
              <div className="mt-2">
                <p className="text-xs opacity-90">
                  Model: {predictions.best_model.replace('_', ' ')}
                </p>
                <p className={`text-xs font-semibold ${predictions.meets_accuracy_threshold ? 'text-green-200' : 'text-orange-200'}`}>
                  Accuracy: {(predictions.model_accuracy * 100).toFixed(1)}%
                  {predictions.meets_accuracy_threshold ? ' ✓' : ' ⚠️'}
                </p>
              </div>
            </div>
            <div className="bg-white bg-opacity-20 p-3 rounded-full">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryCards;
