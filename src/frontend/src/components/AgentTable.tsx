/**
 * AgentTable component
 *
 * Displays a sortable table of individual developer/AI agent statistics.
 */

import { useState, useMemo } from 'react'
import {
  ChevronUpIcon,
  ChevronDownIcon,
  UserIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import type { DeveloperStats } from '../types'

export interface AgentTableProps {
  agents: DeveloperStats[]
  filterType?: 'all' | 'human' | 'ai'
}

type SortField = 'id' | 'type' | 'prs_created' | 'prs_merged' | 'prs_reverted' | 'reviews_completed' | 'current_productivity'
type SortDirection = 'asc' | 'desc'

export default function AgentTable({ agents, filterType = 'all' }: AgentTableProps) {
  const [sortField, setSortField] = useState<SortField>('prs_created')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [selectedType, setSelectedType] = useState<'all' | 'human' | 'ai'>(filterType)

  // Filter agents by type
  const filteredAgents = useMemo(() => {
    if (selectedType === 'all') return agents
    return agents.filter((agent) => agent.type === selectedType)
  }, [agents, selectedType])

  // Sort agents
  const sortedAgents = useMemo(() => {
    const sorted = [...filteredAgents].sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      const aNum = Number(aValue) || 0
      const bNum = Number(bValue) || 0
      return sortDirection === 'asc' ? aNum - bNum : bNum - aNum
    })

    return sorted
  }, [filteredAgents, sortField, sortDirection])

  // Toggle sort
  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // Calculate success rate
  const getSuccessRate = (agent: DeveloperStats): number => {
    if (agent.prs_created === 0) return 0
    return agent.prs_merged / agent.prs_created
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      {/* Header with filters */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Developer Statistics
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({sortedAgents.length} {sortedAgents.length === 1 ? 'agent' : 'agents'})
            </span>
          </h3>

          {/* Type filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedType('all')}
              className={clsx(
                'px-3 py-1 rounded text-sm font-medium transition-colors',
                selectedType === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              All
            </button>
            <button
              onClick={() => setSelectedType('human')}
              className={clsx(
                'px-3 py-1 rounded text-sm font-medium transition-colors flex items-center gap-1',
                selectedType === 'human'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              <UserIcon className="h-4 w-4" />
              Human
            </button>
            <button
              onClick={() => setSelectedType('ai')}
              className={clsx(
                'px-3 py-1 rounded text-sm font-medium transition-colors flex items-center gap-1',
                selectedType === 'ai'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              <CpuChipIcon className="h-4 w-4" />
              AI
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <SortableHeader
                label="Agent ID"
                field="id"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <SortableHeader
                label="Type"
                field="type"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Level/Model
              </th>
              <SortableHeader
                label="PRs Created"
                field="prs_created"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <SortableHeader
                label="PRs Merged"
                field="prs_merged"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <SortableHeader
                label="PRs Reverted"
                field="prs_reverted"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Success Rate
              </th>
              <SortableHeader
                label="Reviews"
                field="reviews_completed"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
              <SortableHeader
                label="Productivity"
                field="current_productivity"
                currentField={sortField}
                direction={sortDirection}
                onSort={handleSort}
              />
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedAgents.map((agent) => {
              const successRate = getSuccessRate(agent)

              return (
                <tr key={agent.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {agent.id.substring(0, 8)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      className={clsx(
                        'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium',
                        agent.type === 'human'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      )}
                    >
                      {agent.type === 'human' ? (
                        <UserIcon className="h-3 w-3" />
                      ) : (
                        <CpuChipIcon className="h-3 w-3" />
                      )}
                      {agent.type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {agent.experience_level || agent.model_type || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {agent.prs_created}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                    {agent.prs_merged}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                    {agent.prs_reverted}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[80px]">
                        <div
                          className={clsx(
                            'h-2 rounded-full transition-all',
                            successRate >= 0.9
                              ? 'bg-green-500'
                              : successRate >= 0.7
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          )}
                          style={{ width: `${successRate * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-600">
                        {(successRate * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {agent.reviews_completed}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      className={clsx(
                        'font-medium',
                        agent.current_productivity >= 0.9
                          ? 'text-green-600'
                          : agent.current_productivity >= 0.5
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      )}
                    >
                      {(agent.current_productivity * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Empty state */}
      {sortedAgents.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No agents found</p>
        </div>
      )}
    </div>
  )
}

/**
 * Sortable table header component
 */
interface SortableHeaderProps {
  label: string
  field: SortField
  currentField: SortField
  direction: SortDirection
  onSort: (field: SortField) => void
}

function SortableHeader({
  label,
  field,
  currentField,
  direction,
  onSort,
}: SortableHeaderProps) {
  const isActive = field === currentField

  return (
    <th
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors select-none"
      onClick={() => onSort(field)}
    >
      <div className="flex items-center gap-1">
        {label}
        <div className="flex flex-col">
          <ChevronUpIcon
            className={clsx(
              'h-3 w-3 -mb-1',
              isActive && direction === 'asc' ? 'text-primary-600' : 'text-gray-400'
            )}
          />
          <ChevronDownIcon
            className={clsx(
              'h-3 w-3 -mt-1',
              isActive && direction === 'desc' ? 'text-primary-600' : 'text-gray-400'
            )}
          />
        </div>
      </div>
    </th>
  )
}
