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
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatSnackBar} from '@angular/material/snack-bar';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {switchMap} from 'rxjs/operators';
import {of} from 'rxjs';

import {ChatHistorySidebarComponent} from '../chat-history-sidebar/chat-history-sidebar.component';
import {SimplifiedChatComponent} from '../simplified-chat/simplified-chat.component';
import {PlatformService, AppInfo} from '../../core/services/platform.service';
import {SessionService} from '../../core/services/session.service';

@Component({
  selector: 'app-chatbot-page',
  templateUrl: './chatbot-page.component.html',
  styleUrl: './chatbot-page.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatToolbarModule,
    ChatHistorySidebarComponent,
    SimplifiedChatComponent
  ]
})
export class ChatbotPageComponent implements OnInit {
  appName = '';
  appDisplayName = '';
  appDescription = '';
  isLoading = true;
  error: string | null = null;
  userId = 'user';
  currentSessionId = '';
  
  appData: AppInfo | null = null;
  sidebarVisible = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private destroyRef: DestroyRef,
    private platformService: PlatformService,
    private sessionService: SessionService,
    private snackBar: MatSnackBar
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
          if (data) {
            this.appData = data;
            this.appDisplayName = this.platformService.getAppDisplayName(data);
            this.appDescription = data.description;
            this.createInitialSession();
          } else {
            this.error = `无法找到应用 "${this.appName}"`;
          }
          this.isLoading = false;
        },
        error: (err) => {
          this.error = `无法加载应用 "${this.appName}"`;
          this.isLoading = false;
          console.error('Error loading app:', err);
        }
      });
  }

  private loadAppData(appName: string) {
    return this.platformService.getApp(appName).pipe(
      switchMap(app => {
        if (app) {
          return of(app);
        }
        // Fallback to mock data for development
        return this.getMockAppData(appName);
      })
    );
  }

  private getMockAppData(appName: string) {
    const mockApps: {[key: string]: AppInfo} = {
      'adk_demo': {
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
      'assistant': {
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
      }
    };

    return of(mockApps[appName] || null);
  }

  private createInitialSession(): void {
    this.sessionService.createSession(this.userId, this.appName)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (session) => {
          this.currentSessionId = session.id;
        },
        error: (err) => {
          console.error('Error creating initial session:', err);
          // Generate a mock session ID for development
          this.currentSessionId = `session_${Date.now()}`;
        }
      });
  }

  onSessionSelected(sessionId: string): void {
    this.currentSessionId = sessionId;
  }

  onNewSessionRequested(): void {
    this.sessionService.createSession(this.userId, this.appName)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (session) => {
          this.currentSessionId = session.id;
          this.snackBar.open('新建对话成功', '确定', { duration: 2000 });
        },
        error: (err) => {
          console.error('Error creating new session:', err);
          this.snackBar.open('新建对话失败', '确定', { duration: 3000 });
        }
      });
  }

  onSessionDeleted(sessionId: string): void {
    if (sessionId === this.currentSessionId) {
      // If current session was deleted, create a new one
      this.onNewSessionRequested();
    }
  }

  onMessageCountChanged(count: number): void {
    // This can be used to update UI or analytics
    console.log(`Message count changed: ${count}`);
  }

  toggleSidebar(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  goToHome(): void {
    this.router.navigate(['/']);
  }
}