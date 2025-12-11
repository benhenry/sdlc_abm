/**
 * MetricCard component
 *
 * Displays a single metric with optional formatting, trend indicator, and color coding.
 */

import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'
import clsx from 'clsx'

export interface MetricCardProps {
  label: string
  value: number | string
  format?: 'number' | 'percent' | 'currency' | 'days' | 'custom'
  customSuffix?: string
  decimals?: number
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: number
  colorScheme?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  icon?: React.ReactNode
  description?: string
}

export default function MetricCard({
  label,
  value,
  format = 'number',
  customSuffix,
  decimals = 1,
  trend,
  trendValue,
  colorScheme = 'default',
  size = 'md',
  icon,
  description,
}: MetricCardProps) {
  // Format value based on format type
  const formattedValue = formatValue(value, format, decimals, customSuffix)

  // Color schemes
  const colorClasses = {
    default: 'text-gray-900',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600',
    info: 'text-blue-600',
  }

  // Size classes
  const sizeClasses = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-3xl',
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {icon && <div className="text-gray-400">{icon}</div>}
            <p className="text-sm font-medium text-gray-600">{label}</p>
          </div>
          <p className={clsx('font-bold mt-1', sizeClasses[size], colorClasses[colorScheme])}>
            {formattedValue}
          </p>
          {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
        </div>

        {/* Trend indicator */}
        {trend && (
          <div
            className={clsx(
              'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium',
              trend === 'up' && 'bg-green-100 text-green-700',
              trend === 'down' && 'bg-red-100 text-red-700',
              trend === 'neutral' && 'bg-gray-100 text-gray-700'
            )}
          >
            {trend === 'up' && <ArrowUpIcon className="h-3 w-3" />}
            {trend === 'down' && <ArrowDownIcon className="h-3 w-3" />}
            {trendValue !== undefined && <span>{formatTrendValue(trendValue)}</span>}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Format value based on type
 */
function formatValue(
  value: number | string,
  format: string,
  decimals: number,
  customSuffix?: string
): string {
  if (typeof value === 'string') {
    return value
  }

  switch (format) {
    case 'number':
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: decimals,
      })

    case 'percent':
      return `${(value * 100).toFixed(decimals)}%`

    case 'currency':
      return `$${value.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`

    case 'days':
      return `${value.toFixed(decimals)} ${value === 1 ? 'day' : 'days'}`

    case 'custom':
      return `${value.toFixed(decimals)}${customSuffix || ''}`

    default:
      return value.toString()
  }
}

/**
 * Format trend value
 */
function formatTrendValue(value: number): string {
  const formatted = Math.abs(value).toFixed(1)
  return value > 0 ? `+${formatted}%` : `${formatted}%`
}
