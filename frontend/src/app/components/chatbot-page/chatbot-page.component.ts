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

import {Component, OnInit, DestroyRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ActivatedRoute, Router, Params} from '@angular/router';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatToolbarModule} from '@angular/material/toolbar';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {switchMap} from 'rxjs/operators';
import {of} from 'rxjs';

@Component({
  selector: 'app-chatbot-page',
  templateUrl: './chatbot-page.component.html',
  styleUrl: './chatbot-page.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatToolbarModule
  ]
})
export class ChatbotPageComponent implements OnInit {
  appName = '';
  appDisplayName = '';
  appDescription = '';
  isLoading = true;
  error: string | null = null;

  // Mock app data - will be loaded from API
  appData: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private destroyRef: DestroyRef
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        switchMap((params: Params) => {
          this.appName = params['name'];
          return this.loadAppData(this.appName);
        })
      )
      .subscribe({
        next: (data) => {
          this.appData = data;
          this.appDisplayName = data.displayName;
          this.appDescription = data.description;
          this.isLoading = false;
        },
        error: (err) => {
          this.error = `无法加载应用 "${this.appName}"`;
          this.isLoading = false;
          console.error('Error loading app:', err);
        }
      });
  }

  loadAppData(appName: string) {
    // Mock data - will be replaced with API call
    const mockApps: {[key: string]: any} = {
      'adk_demo': {
        name: 'adk_demo',
        displayName: 'ADK Demo',
        description: 'ADK Demo，可以回答关于纽约(New York City)的天气问题',
        appType: 'chatbot',
        capabilities: ['天气查询', '问答', '对话'],
        features: ['voice', 'file_upload'],
        theme: 'modern',
        layout: 'chat'
      },
      'assistant': {
        name: 'assistant',
        displayName: '通用助手',
        description: '通用AI助手，可以回答各种问题',
        appType: 'chatbot',
        capabilities: ['文本生成', '问答', '对话', '翻译', '总结'],
        features: ['voice', 'file_upload', 'code_execution'],
        theme: 'modern',
        layout: 'chat'
      }
    };

    return of(mockApps[appName] || null);
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  goToHome(): void {
    this.router.navigate(['/']);
  }

  getFeatureLabel(feature: string): string {
    const featureLabels: {[key: string]: string} = {
      'voice': '语音支持',
      'file_upload': '文件上传',
      'code_execution': '代码执行'
    };
    return featureLabels[feature] || feature;
  }

  hasFeature(feature: string): boolean {
    return this.appData?.features?.includes(feature) || false;
  }
}