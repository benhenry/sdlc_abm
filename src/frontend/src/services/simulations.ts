/**
 * Simulation API service
 *
 * Operations for running and monitoring simulations.
 */

import apiClient from './api'
import type { SimulationRun, SimulationStatus } from '../types'

export interface RunSimulationParams {
  scenario_id?: string
  config_json: Record<string, any>
}

export const simulationService = {
  /**
   * Start a new simulation
   */
  async run(params: RunSimulationParams): Promise<SimulationRun> {
    const response = await apiClient.post('/api/simulations/run', params)
    return response.data
  },

  /**
   * List simulation runs
   */
  async list(
    skip = 0,
    limit = 100,
    statusFilter?: SimulationStatus
  ): Promise<{ simulations: SimulationRun[]; total: number }> {
    const response = await apiClient.get('/api/simulations', {
      params: {
        skip,
        limit,
        status_filter: statusFilter,
      },
    })
    return response.data
  },

  /**
   * Get simulation by ID
   */
  async get(id: string): Promise<SimulationRun> {
    const response = await apiClient.get(`/api/simulations/${id}`)
    return response.data
  },

  /**
   * Cancel a running simulation
   */
  async cancel(id: string): Promise<SimulationRun> {
    const response = await apiClient.post(`/api/simulations/${id}/cancel`)
    return response.data
  },

  /**
   * Delete simulation
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/simulations/${id}`)
  },
}
