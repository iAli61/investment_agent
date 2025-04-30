import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../../utils/formatters';

/**
 * CashFlowChart component for visualizing property cash flow data
 * 
 * @param {object} props Component props
 * @param {object} props.cashFlowData The cash flow data object
 * @param {string} props.height Chart height (default: 400px)
 */
const CashFlowChart = ({ cashFlowData, height = 400 }) => {
  // Transform data for the chart
  const chartData = [
    {
      name: 'Income',
      value: cashFlowData.monthlyIncome,
      color: '#4CAF50'  // green
    },
    {
      name: 'Expenses',
      value: -Math.abs(cashFlowData.monthlyExpenses),
      color: '#F44336'  // red
    },
    {
      name: 'Mortgage',
      value: -Math.abs(cashFlowData.monthlyMortgage),
      color: '#FF9800'  // orange
    },
    {
      name: 'Tax Savings',
      value: cashFlowData.monthlyTaxSavings,
      color: '#2196F3'  // blue
    },
    {
      name: 'Net Cash Flow',
      value: cashFlowData.monthlyCashFlowAfterTax,
      color: '#9C27B0'  // purple
    }
  ];

  // Custom tooltip to display formatted currency values
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 shadow-md rounded-md">
          <p className="font-medium text-gray-700">{data.name}</p>
          <p className="text-sm text-gray-900">{formatCurrency(Math.abs(data.value))}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Monthly Cash Flow</h3>
      
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" />
          <YAxis 
            tickFormatter={(value) => formatCurrency(value, '€', 'de-DE')} 
            label={{ 
              value: 'Amount (€)', 
              angle: -90, 
              position: 'insideLeft',
              style: { textAnchor: 'middle' }
            }} 
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey="value" 
            name="Amount" 
            fill="#8884d8" 
            isAnimationActive={true}
            animationDuration={1000}
            animationEasing="ease-out"
            // Use individual colors for each bar
            fill={(entry) => entry.color}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CashFlowChart;