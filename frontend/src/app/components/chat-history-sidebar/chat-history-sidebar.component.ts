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

import {Component, OnInit, Input, Output, EventEmitter, DestroyRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {MatMenuModule} from '@angular/material/menu';
import {MatTooltipModule} from '@angular/material/tooltip';
import {MatDialog} from '@angular/material/dialog';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {Observable, of} from 'rxjs';
import {SessionService} from '../../core/services/session.service';
import {Session} from '../../core/models/Session';
import {DeleteSessionDialogComponent, DeleteSessionDialogData} from '../session-tab/delete-session-dialog/delete-session-dialog.component';

export interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
}

@Component({
  selector: 'app-chat-history-sidebar',
  templateUrl: './chat-history-sidebar.component.html',
  styleUrl: './chat-history-sidebar.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatMenuModule,
    MatTooltipModule
  ]
})
export class ChatHistorySidebarComponent implements OnInit {
  @Input() appName: string = '';
  @Input() userId: string = 'user';
  @Input() currentSessionId: string = '';
  @Output() sessionSelected = new EventEmitter<string>();
  @Output() newSessionRequested = new EventEmitter<void>();
  @Output() sessionDeleted = new EventEmitter<string>();

  sessions: ChatSession[] = [];
  isLoading = false;

  constructor(
    private sessionService: SessionService,
    private dialog: MatDialog,
    private destroyRef: DestroyRef
  ) {}

  ngOnInit(): void {
    this.loadSessions();
  }

  loadSessions(): void {
    if (!this.appName || !this.userId) return;

    this.isLoading = true;
    this.sessionService.listSessions(this.userId, this.appName)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (response) => {
          this.sessions = this.transformSessions(response.sessions || []);
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Error loading sessions:', err);
          this.isLoading = false;
          // Use mock data for development
          this.sessions = this.getMockSessions();
        }
      });
  }

  private transformSessions(sessionData: any[]): ChatSession[] {
    return sessionData.map(session => ({
      id: session.id,
      title: this.generateSessionTitle(session),
      lastMessage: this.getLastMessage(session),
      timestamp: new Date(session.updatedAt || session.createdAt),
      messageCount: session.events ? session.events.length : 0
    })).sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  private generateSessionTitle(session: any): string {
    if (session.title) return session.title;
    
    // Generate title from first user message
    const userMessages = session.events?.filter((event: any) => 
      event.author === 'user' && event.content?.parts?.some((part: any) => part.text)
    );
    
    if (userMessages && userMessages.length > 0) {
      const firstMessage = userMessages[0].content.parts.find((part: any) => part.text);
      if (firstMessage?.text) {
        const title = firstMessage.text.trim().substring(0, 30);
        return title.length < firstMessage.text.trim().length ? title + '...' : title;
      }
    }
    
    return `对话 ${new Date(session.createdAt).toLocaleDateString()}`;
  }

  private getLastMessage(session: any): string {
    if (!session.events || session.events.length === 0) return '新对话';
    
    const lastEvent = session.events[session.events.length - 1];
    if (lastEvent.content?.parts) {
      const textPart = lastEvent.content.parts.find((part: any) => part.text);
      if (textPart?.text) {
        const message = textPart.text.trim().substring(0, 50);
        return message.length < textPart.text.trim().length ? message + '...' : message;
      }
    }
    
    return lastEvent.author === 'user' ? '用户消息' : 'AI回复';
  }

  private getMockSessions(): ChatSession[] {
    const now = new Date();
    return [
      {
        id: 'mock-session-1',
        title: '如何学习Angular开发？',
        lastMessage: '推荐从官方文档开始，然后做实际项目...',
        timestamp: new Date(now.getTime() - 1000 * 60 * 30), // 30分钟前
        messageCount: 12
      },
      {
        id: 'mock-session-2', 
        title: 'TypeScript类型定义问题',
        lastMessage: '这个问题可以通过接口定义来解决...',
        timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 2), // 2小时前
        messageCount: 8
      },
      {
        id: 'mock-session-3',
        title: '代码重构最佳实践',
        lastMessage: '重构时要遵循SOLID原则...',
        timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24), // 1天前
        messageCount: 15
      }
    ];
  }

  onNewSession(): void {
    this.newSessionRequested.emit();
  }

  onSessionClick(sessionId: string): void {
    if (sessionId !== this.currentSessionId) {
      this.sessionSelected.emit(sessionId);
    }
  }

  onDeleteSession(event: Event, sessionId: string): void {
    event.stopPropagation();
    
    const session = this.sessions.find(s => s.id === sessionId);
    const dialogData: DeleteSessionDialogData = {
      title: '确认删除',
      message: `确定要删除对话 "${session?.title || sessionId}"吗？`,
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    };

    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      width: '400px',
      data: dialogData,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.deleteSession(sessionId);
      }
    });
  }

  private deleteSession(sessionId: string): void {
    this.sessionService.deleteSession(this.userId, this.appName, sessionId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.sessions = this.sessions.filter(s => s.id !== sessionId);
          this.sessionDeleted.emit(sessionId);
        },
        error: (err) => {
          console.error('Error deleting session:', err);
        }
      });
  }

  formatTimestamp(timestamp: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return diffMinutes < 1 ? '刚刚' : `${diffMinutes}分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return timestamp.toLocaleDateString('zh-CN');
    }
  }

  refreshSessions(): void {
    this.loadSessions();
  }

  trackBySessionId = (index: number, session: ChatSession) => session.id;
}