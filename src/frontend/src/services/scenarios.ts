/**
 * Scenario API service
 *
 * CRUD operations for simulation scenarios.
 */

import apiClient from './api'
import type { Scenario, ScenarioCreate, ScenarioUpdate, Template } from '../types'

export const scenarioService = {
  /**
   * List all scenarios
   */
  async list(skip = 0, limit = 100): Promise<{ scenarios: Scenario[]; total: number }> {
    const response = await apiClient.get('/api/scenarios', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Get scenario by ID
   */
  async get(id: string): Promise<Scenario> {
    const response = await apiClient.get(`/api/scenarios/${id}`)
    return response.data
  },

  /**
   * Create new scenario
   */
  async create(data: ScenarioCreate): Promise<Scenario> {
    const response = await apiClient.post('/api/scenarios', data)
    return response.data
  },

  /**
   * Update existing scenario
   */
  async update(id: string, data: ScenarioUpdate): Promise<Scenario> {
    const response = await apiClient.put(`/api/scenarios/${id}`, data)
    return response.data
  },

  /**
   * Delete scenario
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/scenarios/${id}`)
  },

  /**
   * Create scenario from template
   */
  async createFromTemplate(templateName: string, scenarioName: string): Promise<Scenario> {
    const response = await apiClient.post('/api/scenarios/from-template', null, {
      params: { template_name: templateName, scenario_name: scenarioName },
    })
    return response.data
  },

  /**
   * List available templates
   */
  async listTemplates(): Promise<{ templates: Template[]; total: number }> {
    const response = await apiClient.get('/api/templates')
    return response.data
  },

  /**
   * Get specific template
   */
  async getTemplate(name: string): Promise<Template> {
    const response = await apiClient.get(`/api/templates/${name}`)
    return response.data
  },
}
