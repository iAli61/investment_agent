import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatPercent } from '../../utils/formatters';

/**
 * ROIChart component for visualizing return on investment metrics
 * 
 * @param {object} props Component props
 * @param {object} props.metrics The investment metrics data
 * @param {number} props.height Chart height (default: 400px)
 */
const ROIChart = ({ metrics, height = 400 }) => {
  // Transform data for the chart
  const chartData = [
    {
      name: 'Cap Rate',
      value: metrics.capRate,
      color: '#4CAF50'  // green
    },
    {
      name: 'Cash-on-Cash',
      value: metrics.cashOnCash,
      color: '#2196F3'  // blue
    },
    {
      name: 'ROI',
      value: metrics.roi,
      color: '#9C27B0'  // purple
    }
  ];

  // Custom tooltip to display formatted percentage values
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 shadow-md rounded-md">
          <p className="font-medium text-gray-700">{data.name}</p>
          <p className="text-sm text-gray-900">{formatPercent(data.value / 100)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Investment Return Metrics</h3>
      
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" />
          <YAxis 
            tickFormatter={(value) => `${value}%`} 
            label={{ 
              value: 'Percentage (%)', 
              angle: -90, 
              position: 'insideLeft',
              style: { textAnchor: 'middle' }
            }} 
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey="value" 
            name="Return" 
            fill="#8884d8" 
            isAnimationActive={true}
            animationDuration={1000}
            animationEasing="ease-out"
            // Use individual colors for each bar
            fill={(entry) => entry.color}
            radius={[4, 4, 0, 0]}  // Rounded top corners
          />
        </BarChart>
      </ResponsiveContainer>
      
      <div className="grid grid-cols-3 gap-4 mt-4 text-xs text-gray-600">
        <div>
          <p className="font-medium">Cap Rate</p>
          <p>Net Operating Income / Property Value</p>
        </div>
        <div>
          <p className="font-medium">Cash-on-Cash Return</p>
          <p>Annual Cash Flow / Cash Invested</p>
        </div>
        <div>
          <p className="font-medium">ROI (Return on Investment)</p>
          <p>Total Return / Total Investment</p>
        </div>
      </div>
    </div>
  );
};

export default ROIChart;