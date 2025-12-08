import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { PlusIcon, BeakerIcon } from '@heroicons/react/24/outline'
import { scenarioService } from '../services/scenarios'
import type { Scenario } from '../types'

export default function ScenarioLibrary() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadScenarios()
  }, [])

  async function loadScenarios() {
    try {
      const data = await scenarioService.list()
      setScenarios(data.scenarios)
    } catch (error) {
      console.error('Failed to load scenarios:', error)
    } finally {
      setLoading(false)
    }
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scenario Library</h1>
          <p className="text-gray-600 mt-1">Manage your simulation scenarios</p>
        </div>
        <Link to="/scenarios/new" className="btn-primary flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          New Scenario
        </Link>
      </div>

      {scenarios.length === 0 ? (
        <div className="card text-center py-12">
          <BeakerIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No scenarios yet</h3>
          <p className="text-gray-600 mb-6">
            Get started by creating your first simulation scenario
          </p>
          <Link to="/scenarios/new" className="btn-primary inline-flex items-center">
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Scenario
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarios.map((scenario) => (
            <div key={scenario.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900">{scenario.name}</h3>
              </div>
              {scenario.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {scenario.description}
                </p>
              )}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                <span className="text-xs text-gray-500">
                  {formatDate(scenario.created_at)}
                </span>
                <Link
                  to={`/scenarios/${scenario.id}/edit`}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
