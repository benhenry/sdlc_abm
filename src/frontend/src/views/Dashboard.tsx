import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BeakerIcon,
  RectangleStackIcon,
  ArrowsRightLeftIcon,
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { simulationService } from '../services/simulations'
import { scenarioService } from '../services/scenarios'
import type { SimulationRun, Scenario } from '../types'
import clsx from 'clsx'

export default function Dashboard() {
  const [recentSimulations, setRecentSimulations] = useState<SimulationRun[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const [simsData, scenariosData] = await Promise.all([
        simulationService.list(0, 10),
        scenarioService.list(0, 10),
      ])

      setRecentSimulations(simsData.simulations)
      setScenarios(scenariosData.scenarios)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'running':
        return <PlayIcon className="h-5 w-5 text-blue-500 animate-pulse" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
    }
  }

  function getStatusText(status: string) {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome banner */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to SDLC SimLab</h1>
        <p className="text-primary-100 text-lg">
          Agent-based modeling for software development team dynamics
        </p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/scenarios/new"
          className="card hover:shadow-md transition-shadow cursor-pointer group"
        >
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg group-hover:bg-primary-200 transition-colors">
              <BeakerIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">New Scenario</h3>
              <p className="text-sm text-gray-600">Create a new simulation</p>
            </div>
          </div>
        </Link>

        <Link
          to="/scenarios"
          className="card hover:shadow-md transition-shadow cursor-pointer group"
        >
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
              <RectangleStackIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Scenarios</h3>
              <p className="text-sm text-gray-600">{scenarios.length} saved scenarios</p>
            </div>
          </div>
        </Link>

        <Link
          to="/comparisons/new"
          className="card hover:shadow-md transition-shadow cursor-pointer group"
        >
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
              <ArrowsRightLeftIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Compare</h3>
              <p className="text-sm text-gray-600">Compare scenarios</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent simulations */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Recent Simulations</h2>
          <Link
            to="/scenarios"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View all
          </Link>
        </div>

        {recentSimulations.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <BeakerIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg">No simulations yet</p>
            <p className="text-sm">Create your first scenario to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {recentSimulations.map((sim) => (
              <Link
                key={sim.id}
                to={`/simulations/${sim.id}`}
                className="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(sim.status)}
                    <div>
                      <p className="font-medium text-gray-900">
                        Simulation {sim.id.slice(0, 8)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {formatDate(sim.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {getStatusText(sim.status)}
                      </p>
                      {sim.status === 'running' && (
                        <p className="text-xs text-gray-600">
                          {Math.round(sim.progress * 100)}% complete
                        </p>
                      )}
                      {sim.status === 'completed' && sim.results_json?.metrics && (
                        <p className="text-xs text-gray-600">
                          {sim.results_json.metrics.total_prs_merged} PRs merged
                        </p>
                      )}
                    </div>
                    {sim.status === 'running' && (
                      <div className="w-32">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{ width: `${sim.progress * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
