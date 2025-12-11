import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowDownTrayIcon,
  XCircleIcon,
  PlayCircleIcon,
} from '@heroicons/react/24/outline'
import { simulationService } from '../services/simulations'
import { useSimulationWebSocket } from '../services/websocket'
import type { SimulationRun, ProgressUpdate } from '../types'
import ProgressBar from '../components/ProgressBar'
import MetricsDashboard from '../components/MetricsDashboard'
import AgentTable from '../components/AgentTable'
import TimeSeriesChart, { generateWeekLabels } from '../components/TimeSeriesChart'

export default function SimulationResults() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [simulation, setSimulation] = useState<SimulationRun | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Set up WebSocket for live updates
  useSimulationWebSocket(id || '', (update: ProgressUpdate) => {
    console.log('Progress update:', update)

    // Update progress and current metrics in UI
    setSimulation((prev) => {
      if (!prev) return prev

      // Create updated simulation with proper types
      const updated: SimulationRun = {
        ...prev,
        progress: update.progress,
        status: update.status,
      }

      // If we have current metrics, merge them into results
      if (update.current_metrics && prev.results_json) {
        updated.results_json = {
          ...prev.results_json,
          metrics: {
            ...prev.results_json.metrics,
            ...update.current_metrics,
          } as any, // Type assertion needed for partial metrics
        }
      }

      return updated
    })

    // If simulation completed, reload full results
    if (update.status === 'completed' && id) {
      loadSimulation(id)
    }
  })

  useEffect(() => {
    if (id) {
      loadSimulation(id)
    }
  }, [id])

  async function loadSimulation(simulationId: string) {
    try {
      setError(null)
      const data = await simulationService.get(simulationId)
      setSimulation(data)
    } catch (err: any) {
      console.error('Failed to load simulation:', err)
      setError(err.response?.data?.detail || 'Failed to load simulation')
    } finally {
      setLoading(false)
    }
  }

  async function handleCancel() {
    if (!id || !simulation || simulation.status !== 'running') return

    if (confirm('Are you sure you want to cancel this simulation?')) {
      try {
        await simulationService.cancel(id)
        await loadSimulation(id)
      } catch (err: any) {
        console.error('Failed to cancel simulation:', err)
        alert('Failed to cancel simulation')
      }
    }
  }

  async function handleDelete() {
    if (!id) return

    if (confirm('Are you sure you want to delete this simulation?')) {
      try {
        await simulationService.delete(id)
        navigate('/scenarios')
      } catch (err: any) {
        console.error('Failed to delete simulation:', err)
        alert('Failed to delete simulation')
      }
    }
  }

  function handleExportJSON() {
    if (!simulation) return

    const dataStr = JSON.stringify(simulation, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `simulation-${simulation.id}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  function handleExportCSV() {
    if (!simulation?.results_json?.developer_stats) return

    const stats = simulation.results_json.developer_stats
    const headers = [
      'Agent ID',
      'Type',
      'Experience/Model',
      'PRs Created',
      'PRs Merged',
      'PRs Reverted',
      'Reviews Completed',
      'Productivity',
    ]

    const rows = stats.map((agent) => [
      agent.id,
      agent.type,
      agent.experience_level || agent.model_type || '',
      agent.prs_created,
      agent.prs_merged,
      agent.prs_reverted,
      agent.reviews_completed,
      agent.current_productivity,
    ])

    const csvContent = [headers, ...rows].map((row) => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `simulation-${simulation.id}-agents.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  // Generate mock time-series data from metrics
  // In a real implementation, the backend would provide this time-series data
  function generateTimeSeriesData() {
    if (!simulation?.results_json?.metrics || !simulation.config_json) return null

    const durationWeeks = simulation.config_json.duration_weeks || 26
    const totalPRs = simulation.results_json.metrics.total_prs_created
    const humanPRs = simulation.results_json.metrics.human_prs_created
    const aiPRs = simulation.results_json.metrics.ai_prs_created

    // Generate weekly data (simplified - in production, backend would provide actual daily/weekly data)
    const weeks = generateWeekLabels(durationWeeks)
    const totalPRsData = Array.from({ length: durationWeeks }, (_, i) =>
      Math.floor((totalPRs / durationWeeks) * (i + 1))
    )
    const humanPRsData = Array.from({ length: durationWeeks }, (_, i) =>
      Math.floor((humanPRs / durationWeeks) * (i + 1))
    )
    const aiPRsData = Array.from({ length: durationWeeks }, (_, i) =>
      Math.floor((aiPRs / durationWeeks) * (i + 1))
    )

    return {
      weeks,
      totalPRsData,
      humanPRsData,
      aiPRsData,
    }
  }

  const timeSeriesData = generateTimeSeriesData()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <XCircleIcon className="h-16 w-16 mx-auto mb-4 text-red-500" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Simulation</h3>
        <p className="text-gray-600">{error}</p>
        <button
          onClick={() => navigate('/scenarios')}
          className="btn-primary mt-4"
        >
          Back to Scenarios
        </button>
      </div>
    )
  }

  if (!simulation) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600">Simulation not found</p>
      </div>
    )
  }

  const hasResults = simulation.results_json && simulation.results_json.metrics
  const hasAgentStats = simulation.results_json?.developer_stats

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Simulation Results</h1>
          <p className="text-gray-600 mt-1">ID: {simulation.id}</p>
          {simulation.created_at && (
            <p className="text-sm text-gray-500 mt-1">
              Created: {new Date(simulation.created_at).toLocaleString()}
            </p>
          )}
        </div>

        <div className="flex gap-2">
          {simulation.status === 'running' && (
            <button onClick={handleCancel} className="btn-secondary flex items-center gap-2">
              <XCircleIcon className="h-5 w-5" />
              Cancel
            </button>
          )}
          {hasResults && (
            <>
              <button
                onClick={handleExportJSON}
                className="btn-secondary flex items-center gap-2"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                Export JSON
              </button>
              {hasAgentStats && (
                <button
                  onClick={handleExportCSV}
                  className="btn-secondary flex items-center gap-2"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  Export CSV
                </button>
              )}
            </>
          )}
          {simulation.status !== 'running' && (
            <button onClick={handleDelete} className="btn-danger flex items-center gap-2">
              <XCircleIcon className="h-5 w-5" />
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="card">
        <ProgressBar
          progress={simulation.progress}
          status={simulation.status}
          size="lg"
          animated={true}
        />
        {simulation.error_message && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
            <p className="text-sm text-red-800">
              <strong>Error:</strong> {simulation.error_message}
            </p>
          </div>
        )}
      </div>

      {/* Metrics Dashboard */}
      {hasResults && (
        <>
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Metrics Overview</h2>
              {simulation.completed_at && (
                <p className="text-sm text-gray-500">
                  Completed: {new Date(simulation.completed_at).toLocaleString()}
                </p>
              )}
            </div>
            {simulation.results_json && (
              <MetricsDashboard
                metrics={simulation.results_json.metrics}
                showAIMetrics={simulation.results_json.metrics.ai_agents > 0}
              />
            )}
          </div>

          {/* Time Series Charts */}
          {timeSeriesData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TimeSeriesChart
                title="Cumulative PRs Over Time"
                data={[
                  {
                    x: timeSeriesData.weeks,
                    y: timeSeriesData.totalPRsData,
                    name: 'Total PRs',
                    color: '#3b82f6',
                    fillArea: true,
                  },
                ]}
                xAxisLabel="Week"
                yAxisLabel="Total PRs"
                height={350}
              />

              {simulation.results_json && simulation.results_json.metrics.ai_agents > 0 && (
                <TimeSeriesChart
                  title="Human vs AI PR Output"
                  data={[
                    {
                      x: timeSeriesData.weeks,
                      y: timeSeriesData.humanPRsData,
                      name: 'Human PRs',
                      color: '#3b82f6',
                      type: 'line',
                    },
                    {
                      x: timeSeriesData.weeks,
                      y: timeSeriesData.aiPRsData,
                      name: 'AI PRs',
                      color: '#8b5cf6',
                      type: 'line',
                    },
                  ]}
                  xAxisLabel="Week"
                  yAxisLabel="Cumulative PRs"
                  height={350}
                />
              )}
            </div>
          )}

          {/* Agent Statistics Table */}
          {hasAgentStats && simulation.results_json?.developer_stats && simulation.results_json.developer_stats.length > 0 && (
            <AgentTable agents={simulation.results_json.developer_stats} />
          )}
        </>
      )}

      {/* Pending/Running state */}
      {!hasResults && simulation.status === 'pending' && (
        <div className="card text-center py-12">
          <PlayCircleIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Simulation Pending</h3>
          <p className="text-gray-600">
            This simulation is queued and will start soon.
          </p>
        </div>
      )}

      {!hasResults && simulation.status === 'running' && (
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Simulation Running</h3>
          <p className="text-gray-600">
            Results will appear here as the simulation progresses.
          </p>
        </div>
      )}
    </div>
  )
}
