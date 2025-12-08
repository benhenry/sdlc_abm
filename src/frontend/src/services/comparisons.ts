/**
 * Comparison API service
 *
 * Operations for comparing multiple scenarios.
 */

import apiClient from './api'
import type { Comparison, ComparisonCreate } from '../types'

export const comparisonService = {
  /**
   * Create and run a new comparison
   */
  async create(data: ComparisonCreate): Promise<Comparison> {
    const response = await apiClient.post('/api/comparisons', data)
    return response.data
  },

  /**
   * List all comparisons
   */
  async list(skip = 0, limit = 100): Promise<{ comparisons: Comparison[]; total: number }> {
    const response = await apiClient.get('/api/comparisons', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Get comparison by ID
   */
  async get(id: string): Promise<Comparison> {
    const response = await apiClient.get(`/api/comparisons/${id}`)
    return response.data
  },

  /**
   * Delete comparison
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/comparisons/${id}`)
  },
}
