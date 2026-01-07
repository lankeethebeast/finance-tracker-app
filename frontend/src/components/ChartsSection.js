import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const ChartsSection = ({ trends, summary, predictions }) => {
  const trendChartData = {
    labels: trends.map((t) => t.period),
    datasets: [
      {
        label: 'Income',
        data: trends.map((t) => t.income),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Expenses',
        data: trends.map((t) => t.expense),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const categoryChartData = {
    labels: summary.category_breakdown.map((c) => c.category),
    datasets: [
      {
        label: 'Spending by Category',
        data: summary.category_breakdown.map((c) => c.total),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(199, 199, 199, 0.8)',
          'rgba(83, 102, 255, 0.8)',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Income vs Expenses Trend</h3>
        <div style={{ height: '300px' }}>
          <Line data={trendChartData} options={chartOptions} />
        </div>
      </div>

      {summary.category_breakdown.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Spending by Category</h3>
          <div style={{ height: '300px' }}>
            <Doughnut data={categoryChartData} options={chartOptions} />
          </div>
        </div>
      )}

      {predictions && predictions.predictions && (
        <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
          <h3 className="text-lg font-bold text-gray-800 mb-4">30-Day Expense Prediction</h3>
          <div style={{ height: '300px' }}>
            <Line
              data={{
                labels: predictions.predictions.map((p) =>
                  new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                ),
                datasets: [
                  {
                    label: 'Predicted Expenses',
                    data: predictions.predictions.map((p) => p.predicted_amount),
                    borderColor: 'rgb(147, 51, 234)',
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                  },
                ],
              }}
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    display: true,
                    text: `Model Accuracy: ${(predictions.model_accuracy * 100).toFixed(1)}%`,
                  },
                },
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartsSection;
