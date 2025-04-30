/**
 * Formats a number as currency
 * 
 * @param {number} value - The value to format
 * @param {string} currency - The currency symbol (default: €)
 * @param {string} locale - The locale to use (default: de-DE)
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (value, currency = '€', locale = 'de-DE') => {
  if (value == null) return `${currency}0`;
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency === '€' ? 'EUR' : 'USD',
    currencyDisplay: 'symbol',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Formats a number as a percentage
 * 
 * @param {number} value - The value to format (e.g., 0.05 for 5%)
 * @param {number} minimumFractionDigits - Minimum fraction digits (default: 1)
 * @param {number} maximumFractionDigits - Maximum fraction digits (default: 2)
 * @returns {string} - Formatted percentage string
 */
export const formatPercent = (value, minimumFractionDigits = 1, maximumFractionDigits = 2) => {
  if (value == null) return '0%';
  
  return new Intl.NumberFormat('de-DE', {
    style: 'percent',
    minimumFractionDigits,
    maximumFractionDigits
  }).format(value);
};

/**
 * Formats a number as an area measurement
 * 
 * @param {number} value - The value to format
 * @param {string} unit - The unit to use (default: m²)
 * @returns {string} - Formatted area string
 */
export const formatArea = (value, unit = 'm²') => {
  if (value == null) return `0 ${unit}`;
  
  return `${Number(value).toLocaleString('de-DE')} ${unit}`;
};

/**
 * Formats a number with thousand separators
 * 
 * @param {number} value - The value to format
 * @param {number} minimumFractionDigits - Minimum fraction digits (default: 0)
 * @param {number} maximumFractionDigits - Maximum fraction digits (default: 2)
 * @returns {string} - Formatted number string
 */
export const formatNumber = (value, minimumFractionDigits = 0, maximumFractionDigits = 2) => {
  if (value == null) return '0';
  
  return new Intl.NumberFormat('de-DE', {
    minimumFractionDigits,
    maximumFractionDigits
  }).format(value);
};

/**
 * Formats a date
 * 
 * @param {Date|string} date - The date to format
 * @param {string} locale - The locale to use (default: de-DE)
 * @returns {string} - Formatted date string
 */
export const formatDate = (date, locale = 'de-DE') => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(dateObj);
};

/**
 * Truncates text to a specified length and adds ellipsis if needed
 * 
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length before truncation (default: 100)
 * @returns {string} - Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  
  return `${text.substring(0, maxLength)}...`;
};