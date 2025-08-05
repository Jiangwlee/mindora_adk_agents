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

import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSelectModule} from '@angular/material/select';
import {MatChipsModule} from '@angular/material/chips';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {Router} from '@angular/router';
import {PlatformService, AppInfo} from '../../core/services/platform.service';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    FormsModule,
    ReactiveFormsModule
  ]
})
export class HomePageComponent implements OnInit {
  title = 'AI Agent App Platform';
  
  apps: AppInfo[] = [];
  filteredApps: AppInfo[] = [];
  isLoading = false;
  searchQuery = '';
  selectedType = '';
  error: string | null = null;

  appTypes = [
    { value: '', label: '全部类型' },
    { value: 'chatbot', label: 'Chatbot' },
    { value: 'custom', label: 'Custom' }
  ];

  constructor(
    private router: Router,
    private platformService: PlatformService
  ) {}

  ngOnInit(): void {
    this.loadApps();
  }

  loadApps(): void {
    this.isLoading = true;
    this.error = null;
    
    this.platformService.getApps().subscribe({
      next: (apps) => {
        this.apps = apps;
        this.filteredApps = [...this.apps];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading apps:', err);
        this.error = '无法加载应用列表';
        this.isLoading = false;
      }
    });
  }

  filterApps(): void {
    let filtered = [...this.apps];

    // Filter by search query
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(app => 
        app.name.toLowerCase().includes(query) ||
        app.description.toLowerCase().includes(query) ||
        app.capabilities.some(cap => cap.toLowerCase().includes(query))
      );
    }

    // Filter by type
    if (this.selectedType) {
      filtered = filtered.filter(app => app.appType === this.selectedType);
    }

    this.filteredApps = filtered;
  }

  onSearchChange(): void {
    this.filterApps();
  }

  onTypeChange(): void {
    this.filterApps();
  }

  getAppRoute(app: AppInfo): string {
    return this.platformService.getAppRoutePath(app);
  }

  getAppTypeLabel(type: string): string {
    return this.platformService.getAppTypeDisplayName(type);
  }

  getAppTypeIcon(type: string): string {
    return type === 'chatbot' ? 'chat' : 'dashboard';
  }

  getAppDisplayName(app: AppInfo): string {
    return this.platformService.getAppDisplayName(app);
  }

  navigateToApp(app: AppInfo): void {
    this.router.navigate([this.getAppRoute(app)]);
  }

  goToDebug(): void {
    this.router.navigate(['/adk-debug']);
  }

  getFeatureLabel(feature: string): string {
    return this.platformService.getFeatureDisplayName(feature);
  }

  getLayoutLabel(layout: string): string {
    const layoutLabels: {[key: string]: string} = {
      'chat': '聊天',
      'dashboard': '仪表板',
      'custom': '自定义'
    };
    return layoutLabels[layout] || layout;
  }

  getThemeLabel(theme: string): string {
    const themeLabels: {[key: string]: string} = {
      'modern': '现代',
      'classic': '经典'
    };
    return themeLabels[theme] || theme;
  }
}