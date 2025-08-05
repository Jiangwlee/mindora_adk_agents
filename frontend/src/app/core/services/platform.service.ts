/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable, of} from 'rxjs';
import {map, catchError} from 'rxjs/operators';
import {URLUtil} from '../../../utils/url-util';

// Platform API interfaces
export interface AppInfo {
  name: string;
  description: string;
  appType: 'chatbot' | 'custom';
  capabilities: string[];
  uiConfig: UiConfig;
  createdAt: string;
  version?: string;
  author?: string;
  tags?: string[];
}

export interface UiConfig {
  theme: 'modern' | 'classic';
  layout: 'chat' | 'dashboard' | 'custom';
  features: string[];
  colors?: {
    primary: string;
    secondary: string;
  };
}

export interface SessionInfo {
  session_id: string;
  app_name: string;
  user_id: string;
  createdAt: string;
  status: 'active' | 'inactive';
}

export interface AppLaunchRequest {
  app_name: string;
  user_id?: string;
  session_config?: any;
}

export interface AppLaunchResponse {
  session_id: string;
  app_name: string;
  user_id: string;
  createdAt: string;
  status: 'active' | 'inactive';
  session_config?: any;
}

@Injectable({
  providedIn: 'root',
})
export class PlatformService {
  private apiServerDomain = URLUtil.getApiServerBaseUrl();
  private cache = new Map<string, any>();
  private cacheExpiry = 5 * 60 * 1000; // 5 minutes

  constructor(private http: HttpClient) {}

  /**
   * Get all available apps
   */
  getApps(): Observable<AppInfo[]> {
    const cacheKey = 'apps';
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return of(cached);
    }

    return this.http.get<{apps: AppInfo[]}>(`${this.apiServerDomain}/platform/apps`).pipe(
      map(response => {
        const apps = response.apps;
        this.setToCache(cacheKey, apps);
        return apps;
      }),
      catchError(error => {
        console.error('Error fetching apps:', error);
        // Fallback to mock data
        const mockApps: AppInfo[] = [
          {
            name: 'adk_demo',
            description: 'ADK Demo，可以回答关于纽约(New York City)的天气问题',
            appType: 'chatbot',
            capabilities: ['天气查询', '问答', '对话'],
            uiConfig: {
              theme: 'modern',
              layout: 'chat',
              features: ['voice', 'file_upload']
            },
            createdAt: '2025-08-04T10:27:43.184368'
          },
          {
            name: 'assistant',
            description: '通用AI助手，可以回答各种问题',
            appType: 'chatbot',
            capabilities: ['文本生成', '问答', '对话', '翻译', '总结'],
            uiConfig: {
              theme: 'modern',
              layout: 'chat',
              features: ['voice', 'file_upload', 'code_execution']
            },
            createdAt: '2025-08-04T13:50:08.340263'
          },
          {
            name: 'data_analyst',
            description: '专业的数据分析助手，可以处理和分析各种数据',
            appType: 'custom',
            capabilities: ['数据分析', '图表生成', '统计计算', '报告生成'],
            uiConfig: {
              theme: 'modern',
              layout: 'dashboard',
              features: ['file_upload', 'chart_generation', 'data_export'],
              colors: {
                primary: '#1976d2',
                secondary: '#424242'
              }
            },
            createdAt: '2025-08-05T10:00:00.000000'
          }
        ];
        return of(mockApps);
      })
    );
  }

  /**
   * Get app by name
   */
  getApp(name: string): Observable<AppInfo | null> {
    const cacheKey = `app_${name}`;
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return of(cached);
    }

    return this.http.get<AppInfo>(`${this.apiServerDomain}/platform/apps/${name}`).pipe(
      map(response => {
        this.setToCache(cacheKey, response);
        return response;
      }),
      catchError(error => {
        console.error(`Error fetching app ${name}:`, error);
        return of(null);
      })
    );
  }

  /**
   * Launch an app session
   */
  launchApp(request: AppLaunchRequest): Observable<AppLaunchResponse> {
    return this.http.post<AppLaunchResponse>(
      `${this.apiServerDomain}/platform/apps/${request.app_name}/launch`,
      request
    ).pipe(
      catchError(error => {
        console.error('Error launching app:', error);
        // Fallback response
        const fallbackResponse: AppLaunchResponse = {
          session_id: `session_${Date.now()}`,
          app_name: request.app_name,
          user_id: request.user_id || 'default_user',
          createdAt: new Date().toISOString(),
          status: 'active',
          session_config: request.session_config
        };
        return of(fallbackResponse);
      })
    );
  }

  /**
   * Get session information
   */
  getSession(sessionId: string): Observable<SessionInfo | null> {
    return this.http.get<SessionInfo>(`${this.apiServerDomain}/platform/sessions/${sessionId}`).pipe(
      catchError(error => {
        console.error(`Error fetching session ${sessionId}:`, error);
        return of(null);
      })
    );
  }

  /**
   * Update session
   */
  updateSession(sessionId: string, updates: Partial<SessionInfo>): Observable<SessionInfo | null> {
    return this.http.put<SessionInfo>(
      `${this.apiServerDomain}/platform/sessions/${sessionId}`,
      updates
    ).pipe(
      catchError(error => {
        console.error(`Error updating session ${sessionId}:`, error);
        return of(null);
      })
    );
  }

  /**
   * Delete session
   */
  deleteSession(sessionId: string): Observable<boolean> {
    return this.http.delete(`${this.apiServerDomain}/platform/sessions/${sessionId}`).pipe(
      map(() => true),
      catchError(error => {
        console.error(`Error deleting session ${sessionId}:`, error);
        return of(false);
      })
    );
  }

  /**
   * Clean up expired sessions
   */
  cleanupSessions(): Observable<boolean> {
    return this.http.post(`${this.apiServerDomain}/platform/cleanup`, {}).pipe(
      map(() => true),
      catchError(error => {
        console.error('Error cleaning up sessions:', error);
        return of(false);
      })
    );
  }

  /**
   * Get apps by type
   */
  getAppsByType(appType: 'chatbot' | 'custom'): Observable<AppInfo[]> {
    return this.getApps().pipe(
      map(apps => apps.filter(app => app.appType === appType))
    );
  }

  /**
   * Search apps by query
   */
  searchApps(query: string): Observable<AppInfo[]> {
    return this.getApps().pipe(
      map(apps => {
        if (!query) return apps;
        
        const lowerQuery = query.toLowerCase();
        return apps.filter(app => 
          app.name.toLowerCase().includes(lowerQuery) ||
          app.description.toLowerCase().includes(lowerQuery) ||
          app.capabilities.some(cap => cap.toLowerCase().includes(lowerQuery))
        );
      })
    );
  }

  /**
   * Get app display name
   */
  getAppDisplayName(app: AppInfo): string {
    // Convert snake_case or camelCase to display name
    return app.name
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/\b\w/g, l => l.toUpperCase())
      .trim();
  }

  /**
   * Get app type display name
   */
  getAppTypeDisplayName(appType: string): string {
    const typeMap: {[key: string]: string} = {
      'chatbot': 'Chatbot',
      'custom': 'Custom'
    };
    return typeMap[appType] || appType;
  }

  /**
   * Get feature display name
   */
  getFeatureDisplayName(feature: string): string {
    const featureMap: {[key: string]: string} = {
      'voice': '语音支持',
      'file_upload': '文件上传',
      'code_execution': '代码执行',
      'chart_generation': '图表生成',
      'data_export': '数据导出'
    };
    return featureMap[feature] || feature;
  }

  /**
   * Cache management methods
   */
  private getFromCache(key: string): any {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  private setToCache(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Check if app is available
   */
  isAppAvailable(appName: string): Observable<boolean> {
    return this.getApp(appName).pipe(
      map(app => app !== null)
    );
  }

  /**
   * Get app route path
   */
  getAppRoutePath(app: AppInfo): string {
    return `/app/${app.appType}/${app.name}`;
  }
}