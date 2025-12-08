import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ChartBarIcon } from '@heroicons/react/24/outline'
import { simulationService } from '../services/simulations'
import { useSimulationWebSocket } from '../services/websocket'
import type { SimulationRun, ProgressUpdate } from '../types'

export default function SimulationResults() {
  const { id } = useParams<{ id: string }>()
  const [simulation, setSimulation] = useState<SimulationRun | null>(null)
  const [loading, setLoading] = useState(true)

  // Set up WebSocket for live updates
  useSimulationWebSocket(id || '', (update: ProgressUpdate) => {
    console.log('Progress update:', update)
    // Update progress in UI
    if (simulation) {
      setSimulation({
        ...simulation,
        progress: update.progress,
        status: update.status,
      })
    }
  })

  useEffect(() => {
    if (id) {
      loadSimulation(id)
    }
  }, [id])

  async function loadSimulation(simulationId: string) {
    try {
      const data = await simulationService.get(simulationId)
      setSimulation(data)
    } catch (error) {
      console.error('Failed to load simulation:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Simulation Results</h1>
        <p className="text-gray-600 mt-1">ID: {simulation.id}</p>
      </div>

      {/* Status card */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Status</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className="font-medium capitalize">{simulation.status}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Progress:</span>
            <span className="font-medium">{Math.round(simulation.progress * 100)}%</span>
          </div>
          {simulation.status === 'running' && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${simulation.progress * 100}%` }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Results preview */}
      {simulation.results_json && simulation.results_json.metrics && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Key Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total PRs</p>
              <p className="text-2xl font-bold text-gray-900">
                {simulation.results_json.metrics.total_prs_created}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">PRs Merged</p>
              <p className="text-2xl font-bold text-green-600">
                {simulation.results_json.metrics.total_prs_merged}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Cycle Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {simulation.results_json.metrics.avg_cycle_time_days.toFixed(1)} days
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Failure Rate</p>
              <p className="text-2xl font-bold text-red-600">
                {(simulation.results_json.metrics.change_failure_rate * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Placeholder for full visualization */}
      <div className="card text-center py-12">
        <ChartBarIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Full Visualization Coming Soon
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Detailed charts, metrics dashboard, and agent statistics are under development.
        </p>
      </div>
    </div>
  )
}
