import React from 'react';

/**
 * MetricCard component for displaying financial metrics in a card format
 * 
 * @param {object} props Component props
 * @param {string} props.label The label for the metric
 * @param {string} props.value The value to display (usually pre-formatted)
 * @param {string} props.description Optional description of the metric
 * @param {string} props.variant Style variant (default, success, warning, danger)
 * @param {React.ReactNode} props.icon Optional icon to display
 * @param {string} props.trend Optional trend indicator ('up', 'down', 'neutral')
 * @param {string} props.trendValue Optional trend value to display
 */
const MetricCard = ({ 
  label, 
  value, 
  description, 
  variant = 'default',
  icon,
  trend,
  trendValue
}) => {
  // Define variant-specific styles
  const variantStyles = {
    default: {
      container: 'bg-white border-gray-200',
      value: 'text-gray-900',
      label: 'text-gray-500'
    },
    success: {
      container: 'bg-green-50 border-green-200',
      value: 'text-green-600',
      label: 'text-green-800'
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      value: 'text-yellow-600',
      label: 'text-yellow-800'
    },
    danger: {
      container: 'bg-red-50 border-red-200',
      value: 'text-red-600',
      label: 'text-red-800'
    }
  };

  // Define trend-specific styles and icons
  const trendStyles = {
    up: {
      text: 'text-green-600',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      )
    },
    down: {
      text: 'text-red-600',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
        </svg>
      )
    },
    neutral: {
      text: 'text-gray-600',
      icon: (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14" />
        </svg>
      )
    }
  };

  const styles = variantStyles[variant] || variantStyles.default;
  const trendStyle = trend ? (trendStyles[trend] || trendStyles.neutral) : null;

  return (
    <div className={`border rounded-lg p-4 ${styles.container}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className={`text-sm font-medium ${styles.label}`}>{label}</p>
          <p className={`text-xl font-bold mt-1 ${styles.value}`}>{value}</p>
          
          {trend && trendValue && (
            <div className={`flex items-center mt-2 ${trendStyle.text} text-sm`}>
              {trendStyle.icon}
              <span className="ml-1">{trendValue}</span>
            </div>
          )}
          
          {description && (
            <p className="text-xs text-gray-500 mt-2">{description}</p>
          )}
        </div>
        
        {icon && (
          <div className="p-2">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;