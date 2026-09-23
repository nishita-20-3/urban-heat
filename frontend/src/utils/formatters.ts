/**
 * Formats a number to Indian Rupee standard format (e.g. ₹2,55,196.00 or ₹2,55,196)
 */
export function formatINR(val: number, includeDecimals = false): string {
  if (val === undefined || val === null || isNaN(val)) return '₹0';
  
  const rounded = includeDecimals ? val.toFixed(2) : Math.round(val).toString();
  const parts = rounded.split('.');
  let integerPart = parts[0];
  const decimalPart = parts.length > 1 ? `.${parts[1]}` : '';

  const isNegative = integerPart.startsWith('-');
  if (isNegative) {
    integerPart = integerPart.substring(1);
  }

  // Indian Numbering System: Last 3 digits, then groups of 2
  let lastThree = integerPart.slice(-3);
  const otherNumbers = integerPart.slice(0, -3);
  if (otherNumbers !== '') {
    lastThree = ',' + lastThree;
  }
  const formattedInteger = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;

  return `${isNegative ? '-' : ''}₹${formattedInteger}${decimalPart}`;
}

/**
 * Compact Indian Rupee format for large sums (e.g., ₹2.55 Lakh, ₹1.45 Cr)
 */
export function formatINRCompact(val: number): string {
  if (val === undefined || val === null || isNaN(val)) return '₹0';
  const abs = Math.abs(val);
  const sign = val < 0 ? '-' : '';

  if (abs >= 10000000) {
    return `${sign}₹${(abs / 10000000).toFixed(2)} Cr`;
  }
  if (abs >= 100000) {
    return `${sign}₹${(abs / 100000).toFixed(2)} Lakh`;
  }
  if (abs >= 1000) {
    return `${sign}₹${(abs / 1000).toFixed(1)}k`;
  }
  return formatINR(val);
}

/**
 * Formats temperature in Celsius
 */
export function formatTemp(val: number | null | undefined, precision = 1): string {
  if (val === null || val === undefined || isNaN(val)) return '-- °C';
  return `${val.toFixed(precision)} °C`;
}

/**
 * Formats cooling contribution (°C reduction)
 */
export function formatCooling(val: number | null | undefined, precision = 2): string {
  if (val === null || val === undefined || isNaN(val)) return '0.00 °C';
  return `-${val.toFixed(precision)} °C`;
}

/**
 * Formats quantity and unit nicely (e.g. "476.1 sqm", "24 trees")
 */
export function formatQuantity(quantity: number, unit: string): string {
  if (quantity === undefined || quantity === null || isNaN(quantity)) return `0 ${unit}`;
  const formattedNumber = quantity < 10 ? quantity.toFixed(1) : Math.round(quantity).toLocaleString('en-IN');
  return `${formattedNumber} ${unit}`;
}

/**
 * Formats standard numbers with Indian commas
 */
export function formatIndianNumber(val: number): string {
  return new Intl.NumberFormat('en-IN').format(val);
}
