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
import {MatTabsModule} from '@angular/material/tabs';
import {MatChipsModule} from '@angular/material/chips';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {switchMap} from 'rxjs/operators';
import {of} from 'rxjs';

@Component({
  selector: 'app-custom-page',
  templateUrl: './custom-page.component.html',
  styleUrl: './custom-page.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatToolbarModule,
    MatTabsModule,
    MatChipsModule
  ]
})
export class CustomPageComponent implements OnInit {
  appName = '';
  appDisplayName = '';
  appDescription = '';
  isLoading = true;
  error: string | null = null;

  // Mock app data - will be loaded from API
  appData: any = null;
  selectedTab = 0;

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
      'data_analyst': {
        name: 'data_analyst',
        displayName: '数据分析师',
        description: '专业的数据分析助手，可以处理和分析各种数据',
        appType: 'custom',
        capabilities: ['数据分析', '图表生成', '统计计算', '报告生成'],
        features: ['file_upload', 'chart_generation', 'data_export'],
        theme: 'modern',
        layout: 'dashboard',
        colors: {
          primary: '#1976d2',
          secondary: '#424242'
        }
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

  onTabChange(event: any): void {
    this.selectedTab = event.index;
  }

  getFeatureLabel(feature: string): string {
    const featureLabels: {[key: string]: string} = {
      'file_upload': '文件上传',
      'chart_generation': '图表生成',
      'data_export': '数据导出'
    };
    return featureLabels[feature] || feature;
  }

  hasFeature(feature: string): boolean {
    return this.appData?.features?.includes(feature) || false;
  }

  getPrimaryColor(): string {
    return this.appData?.colors?.primary || '#1976d2';
  }

  getSecondaryColor(): string {
    return this.appData?.colors?.secondary || '#424242';
  }
}