/**
 * ProgressBar component
 *
 * Displays simulation progress with real-time updates and status information.
 */

import clsx from 'clsx'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/solid'
import type { SimulationStatus } from '../types'

export interface ProgressBarProps {
  progress: number // 0.0 to 1.0
  status: SimulationStatus
  currentStep?: number
  totalSteps?: number
  showPercentage?: boolean
  showSteps?: boolean
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

export default function ProgressBar({
  progress,
  status,
  currentStep,
  totalSteps,
  showPercentage = true,
  showSteps = true,
  size = 'md',
  animated = true,
}: ProgressBarProps) {
  const percentage = Math.round(progress * 100)

  // Status colors
  const statusColors = {
    pending: 'bg-gray-400',
    running: 'bg-blue-600',
    completed: 'bg-green-600',
    failed: 'bg-red-600',
  }

  // Size classes
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  return (
    <div className="space-y-2">
      {/* Status header */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <StatusBadge status={status} />
          {showSteps && currentStep !== undefined && totalSteps !== undefined && (
            <span className="text-gray-600">
              Step {currentStep} of {totalSteps}
            </span>
          )}
        </div>
        {showPercentage && (
          <span className="font-medium text-gray-900">{percentage}%</span>
        )}
      </div>

      {/* Progress bar */}
      <div className={clsx('w-full bg-gray-200 rounded-full overflow-hidden', sizeClasses[size])}>
        <div
          className={clsx(
            'rounded-full transition-all duration-300',
            statusColors[status],
            animated && status === 'running' && 'animate-pulse'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Additional info for completed/failed */}
      {status === 'completed' && (
        <div className="flex items-center gap-1 text-sm text-green-600">
          <CheckCircleIcon className="h-4 w-4" />
          <span>Simulation completed successfully</span>
        </div>
      )}
      {status === 'failed' && (
        <div className="flex items-center gap-1 text-sm text-red-600">
          <XCircleIcon className="h-4 w-4" />
          <span>Simulation failed</span>
        </div>
      )}
    </div>
  )
}

/**
 * Status badge component
 */
interface StatusBadgeProps {
  status: SimulationStatus
}

function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    pending: {
      label: 'Pending',
      className: 'bg-gray-100 text-gray-700',
    },
    running: {
      label: 'Running',
      className: 'bg-blue-100 text-blue-700',
    },
    completed: {
      label: 'Completed',
      className: 'bg-green-100 text-green-700',
    },
    failed: {
      label: 'Failed',
      className: 'bg-red-100 text-red-700',
    },
  }

  const config = statusConfig[status]

  return (
    <span
      className={clsx(
        'px-2 py-1 rounded text-xs font-medium uppercase',
        config.className
      )}
    >
      {config.label}
    </span>
  )
}
