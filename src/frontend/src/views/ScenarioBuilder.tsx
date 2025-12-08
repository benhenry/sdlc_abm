import { BeakerIcon } from '@heroicons/react/24/outline'

export default function ScenarioBuilder() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Scenario Builder</h1>
        <p className="text-gray-600 mt-1">Create and configure simulation scenarios</p>
      </div>

      <div className="card text-center py-16">
        <BeakerIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Scenario Builder Coming Soon
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          The full scenario builder wizard with team composition, communication settings,
          and technical debt configuration is under development.
        </p>
      </div>
    </div>
  )
}
