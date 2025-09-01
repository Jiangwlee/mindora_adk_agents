/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version?: string;
  uptime?: number;
}

export interface AppInfo {
  name: string;
  description?: string;
  version?: string;
  config?: any;
}

export interface EvaluationSummary {
  total_evals: number;
  passed_evals: number;
  failed_evals: number;
  success_rate: number;
  average_score?: number;
  execution_time?: number;
}

export interface EvaluationDetail {
  eval_id: string;
  status: string;
  score?: number;
  metrics: any;
  execution_time?: number;
  error_message?: string;
}