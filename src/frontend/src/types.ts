/**
 * TypeScript type definitions for SDLC SimLab
 *
 * These types mirror the Pydantic schemas from the backend API.
 */

export type SimulationStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ImportSourceType = 'github' | 'gitlab' | 'csv';

// Scenario types
export interface Scenario {
  id: string;
  name: string;
  description: string | null;
  config_json: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ScenarioCreate {
  name: string;
  description?: string | null;
  config_json: Record<string, any>;
}

export interface ScenarioUpdate {
  name?: string;
  description?: string | null;
  config_json?: Record<string, any>;
}

// Simulation types
export interface SimulationRun {
  id: string;
  scenario_id: string | null;
  status: SimulationStatus;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  results_json: SimulationResults | null;
  config_json: Record<string, any>;
  created_at: string;
}

export interface SimulationResults {
  status: string;
  metrics: SimulationMetrics;
  developer_stats?: DeveloperStats[];
  completed_at?: string;
}

export interface SimulationMetrics {
  // Team composition
  total_developers: number;
  human_developers: number;
  ai_agents: number;
  communication_overhead: number;

  // Overall delivery
  total_prs_created: number;
  total_prs_merged: number;
  total_prs_reverted: number;
  open_prs: number;
  avg_cycle_time_days: number;
  change_failure_rate: number;
  prs_per_week: number;

  // Human-specific
  human_prs_created: number;
  human_prs_merged: number;
  human_prs_reverted: number;
  human_failure_rate: number;
  human_prs_per_week: number;
  human_avg_cycle_time_days: number;

  // AI-specific
  ai_prs_created: number;
  ai_prs_merged: number;
  ai_prs_reverted: number;
  ai_failure_rate: number;
  ai_prs_per_week: number;
  ai_avg_cycle_time_days: number;
  ai_total_cost: number;
  ai_avg_cost_per_pr: number;

  // Technical debt
  tech_debt_count: number;
  tech_debt_productivity_impact: number;
  tech_debt_total_created: number;
  tech_debt_total_paid: number;

  // Incidents
  total_incidents: number;
  active_incidents: number;
  resolved_incidents: number;
  avg_mttr_days: number;
}

export interface DeveloperStats {
  id: string;
  type: 'human' | 'ai';
  experience_level?: string;
  model_type?: string;
  prs_created: number;
  prs_merged: number;
  prs_reverted: number;
  reviews_completed: number;
  current_productivity: number;
}

// Comparison types
export interface Comparison {
  id: string;
  name: string;
  scenario_ids: string[];
  status: SimulationStatus;
  results_json: ComparisonResults | null;
  created_at: string;
  completed_at: string | null;
}

export interface ComparisonResults {
  status: string;
  results: Record<string, SimulationMetrics>;
  insights: string[];
}

export interface ComparisonCreate {
  name: string;
  scenario_ids: string[];
}

// Template types
export interface Template {
  name: string;
  path: string;
  description: string | null;
  config: Record<string, any>;
}

// Import types
export interface ImportedDataset {
  id: string;
  source_type: ImportSourceType;
  source_name: string;
  import_date: string;
  metrics_json: Record<string, any>;
  suggested_config_json: Record<string, any> | null;
}

// WebSocket message types
export interface ProgressUpdate {
  type: 'progress';
  simulation_id: string;
  current_step: number;
  total_steps: number;
  progress: number;
  status: SimulationStatus;
  current_metrics?: Partial<SimulationMetrics>;
}

export interface SimulationCompleted {
  type: 'completed';
  simulation_id: string;
  results: SimulationResults;
}

export interface SimulationError {
  type: 'error';
  simulation_id: string;
  error_message: string;
}

export type WebSocketMessage = ProgressUpdate | SimulationCompleted | SimulationError;

// API response types
export interface ApiError {
  detail: string;
  error_type?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}
