import { ArrowsRightLeftIcon } from '@heroicons/react/24/outline'

export default function ComparisonView() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Scenario Comparison</h1>
        <p className="text-gray-600 mt-1">Compare multiple scenarios side-by-side</p>
      </div>

      <div className="card text-center py-16">
        <ArrowsRightLeftIcon className="h-16 w-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Comparison View Coming Soon
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Multi-scenario comparison with side-by-side metrics, winner indicators,
          and automated insights is under development.
        </p>
      </div>
    </div>
  )
}
