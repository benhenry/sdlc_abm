import { Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  BeakerIcon,
  RectangleStackIcon,
  ArrowsRightLeftIcon,
  ArrowDownTrayIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Scenarios', href: '/scenarios', icon: RectangleStackIcon },
  { name: 'New Scenario', href: '/scenarios/new', icon: BeakerIcon },
  { name: 'Compare', href: '/comparisons/new', icon: ArrowsRightLeftIcon },
  { name: 'Import Data', href: '/import', icon: ArrowDownTrayIcon },
  { name: 'Calibration', href: '/calibration', icon: ChartBarIcon },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200">
        {/* Logo */}
        <div className="flex items-center h-16 px-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary-600">SDLC SimLab</h1>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={clsx(
                    'mr-3 h-5 w-5',
                    isActive ? 'text-primary-700' : 'text-gray-400'
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            v0.2.0 | Phase 2 Alpha
          </p>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Top header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-8">
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">
              {navigation.find((item) => item.href === location.pathname)?.name || 'SDLC SimLab'}
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Agent-Based Software Development Simulation</span>
          </div>
        </header>

        {/* Page content */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
