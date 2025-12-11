/**
 * MetricsDashboard component
 *
 * Displays a grid of metrics organized by category for simulation results.
 */

import {
  UsersIcon,
  CodeBracketIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
} from '@heroicons/react/24/outline'
import MetricCard from './MetricCard'
import type { SimulationMetrics } from '../types'

export interface MetricsDashboardProps {
  metrics: SimulationMetrics
  showAIMetrics?: boolean
}

export default function MetricsDashboard({ metrics, showAIMetrics = true }: MetricsDashboardProps) {
  const hasAI = metrics.ai_agents > 0

  return (
    <div className="space-y-6">
      {/* Team Composition */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <UsersIcon className="h-5 w-5" />
          Team Composition
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Developers"
            value={metrics.total_developers}
            format="number"
            colorScheme="info"
            icon={<UsersIcon className="h-5 w-5" />}
          />
          <MetricCard
            label="Human Developers"
            value={metrics.human_developers}
            format="number"
            colorScheme="default"
          />
          {hasAI && (
            <MetricCard
              label="AI Agents"
              value={metrics.ai_agents}
              format="number"
              colorScheme="info"
            />
          )}
          <MetricCard
            label="Communication Overhead"
            value={metrics.communication_overhead}
            format="percent"
            decimals={1}
            colorScheme={metrics.communication_overhead > 0.5 ? 'warning' : 'default'}
          />
        </div>
      </div>

      {/* Overall Delivery Metrics */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <CodeBracketIcon className="h-5 w-5" />
          Overall Delivery
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total PRs Created"
            value={metrics.total_prs_created}
            format="number"
            colorScheme="default"
            size="lg"
          />
          <MetricCard
            label="PRs Merged"
            value={metrics.total_prs_merged}
            format="number"
            colorScheme="success"
            size="lg"
          />
          <MetricCard
            label="PRs Reverted"
            value={metrics.total_prs_reverted}
            format="number"
            colorScheme={metrics.total_prs_reverted > 0 ? 'danger' : 'default'}
          />
          <MetricCard
            label="Open PRs"
            value={metrics.open_prs}
            format="number"
            colorScheme={metrics.open_prs > 10 ? 'warning' : 'default'}
          />
          <MetricCard
            label="Avg Cycle Time"
            value={metrics.avg_cycle_time_days}
            format="days"
            decimals={1}
            colorScheme={metrics.avg_cycle_time_days > 7 ? 'warning' : 'success'}
            icon={<ClockIcon className="h-5 w-5" />}
          />
          <MetricCard
            label="Change Failure Rate"
            value={metrics.change_failure_rate}
            format="percent"
            decimals={1}
            colorScheme={metrics.change_failure_rate > 0.15 ? 'danger' : 'success'}
            icon={<ExclamationTriangleIcon className="h-5 w-5" />}
          />
          <MetricCard
            label="PRs Per Week"
            value={metrics.prs_per_week}
            format="number"
            decimals={1}
            colorScheme="default"
          />
        </div>
      </div>

      {/* Human Developer Metrics */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Human Developer Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Human PRs Created"
            value={metrics.human_prs_created}
            format="number"
            colorScheme="default"
          />
          <MetricCard
            label="Human PRs Merged"
            value={metrics.human_prs_merged}
            format="number"
            colorScheme="success"
          />
          <MetricCard
            label="Human Failure Rate"
            value={metrics.human_failure_rate}
            format="percent"
            decimals={1}
            colorScheme={metrics.human_failure_rate > 0.15 ? 'danger' : 'success'}
          />
          <MetricCard
            label="Human Avg Cycle Time"
            value={metrics.human_avg_cycle_time_days}
            format="days"
            decimals={1}
            colorScheme={metrics.human_avg_cycle_time_days > 7 ? 'warning' : 'success'}
          />
          <MetricCard
            label="Human PRs/Week"
            value={metrics.human_prs_per_week}
            format="number"
            decimals={1}
            colorScheme="default"
          />
        </div>
      </div>

      {/* AI Agent Metrics */}
      {hasAI && showAIMetrics && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Agent Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="AI PRs Created"
              value={metrics.ai_prs_created}
              format="number"
              colorScheme="info"
            />
            <MetricCard
              label="AI PRs Merged"
              value={metrics.ai_prs_merged}
              format="number"
              colorScheme="success"
            />
            <MetricCard
              label="AI Failure Rate"
              value={metrics.ai_failure_rate}
              format="percent"
              decimals={1}
              colorScheme={metrics.ai_failure_rate > 0.2 ? 'danger' : 'success'}
            />
            <MetricCard
              label="AI Avg Cycle Time"
              value={metrics.ai_avg_cycle_time_days}
              format="days"
              decimals={1}
              colorScheme={metrics.ai_avg_cycle_time_days > 5 ? 'warning' : 'success'}
            />
            <MetricCard
              label="AI PRs/Week"
              value={metrics.ai_prs_per_week}
              format="number"
              decimals={1}
              colorScheme="info"
            />
            <MetricCard
              label="Total AI Cost"
              value={metrics.ai_total_cost}
              format="currency"
              decimals={2}
              colorScheme="default"
              icon={<CurrencyDollarIcon className="h-5 w-5" />}
            />
            <MetricCard
              label="Avg Cost Per PR"
              value={metrics.ai_avg_cost_per_pr}
              format="currency"
              decimals={2}
              colorScheme="default"
              icon={<CurrencyDollarIcon className="h-5 w-5" />}
            />
          </div>
        </div>
      )}

      {/* Technical Debt */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <WrenchScrewdriverIcon className="h-5 w-5" />
          Technical Debt
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Current Tech Debt"
            value={metrics.tech_debt_count}
            format="number"
            colorScheme={metrics.tech_debt_count > 10 ? 'warning' : 'default'}
          />
          <MetricCard
            label="Productivity Impact"
            value={metrics.tech_debt_productivity_impact}
            format="percent"
            decimals={1}
            colorScheme={metrics.tech_debt_productivity_impact > 0.2 ? 'danger' : 'default'}
          />
          <MetricCard
            label="Total Debt Created"
            value={metrics.tech_debt_total_created}
            format="number"
            colorScheme="default"
          />
          <MetricCard
            label="Total Debt Paid"
            value={metrics.tech_debt_total_paid}
            format="number"
            colorScheme="success"
          />
        </div>
      </div>

      {/* Incidents */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <ExclamationTriangleIcon className="h-5 w-5" />
          Incidents
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Incidents"
            value={metrics.total_incidents}
            format="number"
            colorScheme="default"
          />
          <MetricCard
            label="Active Incidents"
            value={metrics.active_incidents}
            format="number"
            colorScheme={metrics.active_incidents > 0 ? 'danger' : 'success'}
          />
          <MetricCard
            label="Resolved Incidents"
            value={metrics.resolved_incidents}
            format="number"
            colorScheme="success"
          />
          <MetricCard
            label="Avg MTTR"
            value={metrics.avg_mttr_days}
            format="days"
            decimals={1}
            colorScheme={metrics.avg_mttr_days > 1 ? 'warning' : 'success'}
            description="Mean Time To Recovery"
          />
        </div>
      </div>
    </div>
  )
}
