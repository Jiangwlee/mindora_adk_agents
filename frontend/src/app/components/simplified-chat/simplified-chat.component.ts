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

import {Component, OnInit, Input, Output, EventEmitter, ViewChild, ElementRef, DestroyRef, inject, ChangeDetectorRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatCardModule} from '@angular/material/card';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatMenuModule} from '@angular/material/menu';
import {MatSnackBar} from '@angular/material/snack-bar';
import {takeUntilDestroyed} from '@angular/core/rxjs-interop';
import {BehaviorSubject, combineLatest} from 'rxjs';

import {AgentService} from '../../core/services/agent.service';
import {SessionService} from '../../core/services/session.service';
import {AgentRunRequest} from '../../core/models/AgentRunRequest';
import {getMediaTypeFromMimetype, MediaType, openBase64InNewTab} from '../artifact-tab/artifact-tab.component';
import {MessageProcessingService, ChatMessage} from '../../core/services/message-processing.service';
import {FileProcessingService, FileWithUrl} from '../../core/services/file-processing.service';
import {ArtifactService} from '../../core/services/artifact.service';
import {DownloadService} from '../../core/services/download.service';
import {MatDialog} from '@angular/material/dialog';
import {ViewImageDialogComponent} from '../view-image-dialog/view-image-dialog.component';
import {OAuthHandlingService} from '../../core/services/oauth-handling.service';
import {LongRunningEventsService, LongRunningEvent} from '../../core/services/long-running-events.service';
import {PendingEventDialogComponent} from '../pending-event-dialog/pending-event-dialog.component';
import {ErrorHandlingService} from '../../core/services/error-handling.service';

// ChatMessage interface is now imported from MessageProcessingService

@Component({
  selector: 'app-simplified-chat',
  templateUrl: './simplified-chat.component.html',
  styleUrl: './simplified-chat.component.scss',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    MatMenuModule
  ]
})
export class SimplifiedChatComponent implements OnInit {
  @Input() appName: string = '';
  @Input() sessionId: string = '';
  @Input() userId: string = 'user';
  @Input() appDisplayName: string = '';
  @Input() appDescription: string = '';
  
  @Output() sessionChanged = new EventEmitter<any>();
  @Output() messageCountChanged = new EventEmitter<number>();

  @ViewChild('autoScroll') private scrollContainer!: ElementRef;

  protected MediaType = MediaType;
  protected openBase64InNewTab = openBase64InNewTab;
  getMediaTypeFromMimetype = getMediaTypeFromMimetype;

  messages: ChatMessage[] = [];
  userInput: string = '';
  selectedFiles: FileWithUrl[] = [];
  isLoading = false;
  artifacts: any[] = [];
  longRunningEvents: LongRunningEvent[] = [];
  functionCallEventId = '';
  
  private streamingTextMessage: ChatMessage | null = null;
  private readonly messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  private readonly scrollInterruptedSubject = new BehaviorSubject(true);
  private readonly isModelThinkingSubject = new BehaviorSubject(false);
  
  private readonly changeDetectorRef = inject(ChangeDetectorRef);

  constructor(
    private agentService: AgentService,
    private sessionService: SessionService,
    private destroyRef: DestroyRef,
    private messageProcessingService: MessageProcessingService,
    private fileProcessingService: FileProcessingService,
    private artifactService: ArtifactService,
    private downloadService: DownloadService,
    private dialog: MatDialog,
    private oauthHandlingService: OAuthHandlingService,
    private longRunningEventsService: LongRunningEventsService,
    private errorHandlingService: ErrorHandlingService
  ) {}

  ngOnInit(): void {
    this.setupMessageHandling();
    this.loadSessionMessages();
    this.setupLongRunningEventsHandling();
  }

  private setupMessageHandling(): void {
    // Handle loading state
    combineLatest([
      this.agentService.getLoadingState(), 
      this.isModelThinkingSubject
    ]).pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(([isLoading, isModelThinking]) => {
      const lastMessage = this.messages[this.messages.length - 1];

      if (isLoading) {
        if (!lastMessage?.isLoading && !this.streamingTextMessage) {
          this.messages.push({ role: 'bot', isLoading: true });
          this.messagesSubject.next(this.messages);
        }
      } else if (lastMessage?.isLoading && !isModelThinking) {
        this.messages.pop();
        this.messagesSubject.next(this.messages);
        this.changeDetectorRef.detectChanges();
      }
    });

    // Handle auto-scroll
    combineLatest([
      this.messagesSubject, 
      this.scrollInterruptedSubject
    ]).pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(([messages, scrollInterrupted]) => {
      if (!scrollInterrupted) {
        setTimeout(() => this.scrollToBottom(), 100);
      }
    });
  }

  private setupLongRunningEventsHandling(): void {
    this.longRunningEventsService.getLongRunningEvents()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(events => {
        this.longRunningEvents = events;
        this.changeDetectorRef.detectChanges();
      });
  }

  private loadSessionMessages(): void {
    if (!this.sessionId || !this.appName || !this.userId) return;

    this.sessionService.getSession(this.userId, this.appName, this.sessionId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (session) => {
          if (session?.events) {
            this.messages = this.messageProcessingService.transformSessionEvents(session.events);
            this.messagesSubject.next(this.messages);
            this.messageCountChanged.emit(this.messages.length);
          }
        },
        error: (err) => {
          this.errorHandlingService.handleSessionError(err, {
            operation: 'Load Session Messages',
            userMessage: '加载历史消息失败'
          });
        }
      });
  }

  // transformSessionEvents method is now handled by MessageProcessingService

  async sendMessage(event?: Event): Promise<void> {
    if (event instanceof KeyboardEvent) {
      if (event.isComposing || event.keyCode === 229) return;
      if (!event.shiftKey) {
        event.preventDefault();
      } else {
        return;
      }
    }

    if (!this.userInput.trim() && this.selectedFiles.length <= 0) return;

    // Setup scroll handling
    if (this.messages.length === 0) {
      this.scrollContainer.nativeElement.addEventListener('wheel', () => {
        this.scrollInterruptedSubject.next(true);
      });
      this.scrollContainer.nativeElement.addEventListener('touchmove', () => {
        this.scrollInterruptedSubject.next(true);
      });
    }
    this.scrollInterruptedSubject.next(false);

    // Add user message
    if (this.userInput.trim()) {
      this.messages.push({
        role: 'user', 
        text: this.userInput,
        timestamp: new Date()
      });
      this.messagesSubject.next(this.messages);
    }

    // Add user attachments
    if (this.selectedFiles.length > 0) {
      const messageAttachments = this.selectedFiles.map(file => ({
        file: file.file,
        url: file.url
      }));
      this.messages.push({ 
        role: 'user', 
        attachments: messageAttachments,
        timestamp: new Date()
      });
      this.messagesSubject.next(this.messages);
    }

    // Prepare request
    const req: AgentRunRequest = {
      appName: this.appName,
      userId: this.userId,
      sessionId: this.sessionId,
      newMessage: {
        role: 'user',
        parts: await this.fileProcessingService.getUserMessageParts(this.userInput, this.selectedFiles)
      },
      streaming: true
    };

    this.selectedFiles = [];
    this.streamingTextMessage = null;

    // Send message
    this.agentService.runSse(req)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: async (chunk) => {
          await this.processStreamChunk(chunk);
        },
        error: (err) => {
          this.errorHandlingService.handleStreamError(err, {
            operation: 'Send Message',
            userMessage: '发送消息失败，请重试'
          });
        },
        complete: () => {
          this.streamingTextMessage = null;
          this.messageCountChanged.emit(this.messages.length);
        }
      });

    // Clear input
    this.userInput = '';
    this.changeDetectorRef.detectChanges();
  }

  private async processStreamChunk(chunk: string): Promise<void> {
    if (chunk.startsWith('{"error"')) {
      this.errorHandlingService.handleStreamError(chunk, {
        operation: 'Process Stream Chunk',
        userMessage: '流式响应错误'
      });
      return;
    }

    try {
      const chunkJson = JSON.parse(chunk);
      
      if (chunkJson.error) {
        this.errorHandlingService.handleStreamError(chunkJson.error, {
          operation: 'Process Stream Chunk',
          userMessage: '服务器返回错误'
        });
        return;
      }

      if (chunkJson.content?.parts) {
        for (const part of chunkJson.content.parts) {
          this.processPart(part, chunkJson);
        }
      }

      // Handle artifact actions
      if (chunkJson.actions?.artifactDelta) {
        for (const key in chunkJson.actions.artifactDelta) {
          if (chunkJson.actions.artifactDelta.hasOwnProperty(key)) {
            this.renderArtifact(key, chunkJson.actions.artifactDelta[key]);
          }
        }
      }

      // Handle long running tool IDs
      if (chunkJson.longRunningToolIds && chunkJson.longRunningToolIds.length > 0) {
        const events = this.longRunningEventsService.extractAsyncFunctionsFromParts(
          chunkJson.longRunningToolIds, 
          chunkJson.content.parts
        );
        this.longRunningEventsService.addLongRunningEvents(events);
        this.functionCallEventId = chunkJson.id;

        // Handle OAuth automatically if detected
        const oauthEvent = this.longRunningEventsService.getFirstPendingOAuthEvent();
        if (oauthEvent) {
          this.handleOAuthFlow(oauthEvent);
        }
      }

      this.changeDetectorRef.detectChanges();
    } catch (error) {
      this.errorHandlingService.handleStreamError(error, {
        operation: 'Parse Stream Chunk',
        userMessage: '解析流式响应失败'
      });
    }
  }

  private processPart(part: any, chunkJson: any): void {
    const result = this.messageProcessingService.processPart(
      part, 
      chunkJson, 
      this.streamingTextMessage,
      this.messages,
      (message: ChatMessage) => this.insertMessageBeforeLoadingMessage(message)
    );
    
    this.streamingTextMessage = result.streamingTextMessage;
    // latestThought and isModelThinking can be used if needed for UI updates
  }

  private insertMessageBeforeLoadingMessage(message: ChatMessage): void {
    const lastMessage = this.messages[this.messages.length - 1];
    if (lastMessage?.isLoading) {
      this.messages.splice(this.messages.length - 1, 0, message);
    } else {
      this.messages.push(message);
    }
    this.messagesSubject.next(this.messages);
  }

  // getUserMessageParts method is now handled by FileProcessingService

  // readFileAsBytes method is now handled by FileProcessingService

  // formatBase64Data method is now handled by FileProcessingService

  onFileSelect(event: Event): void {
    this.selectedFiles = this.fileProcessingService.handleFileSelection(event, this.selectedFiles);
  }

  removeFile(index: number): void {
    this.selectedFiles = this.fileProcessingService.removeFile(this.selectedFiles, index);
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      this.scrollContainer.nativeElement.scrollTo({
        top: this.scrollContainer.nativeElement.scrollHeight,
        behavior: 'smooth'
      });
    });
  }

  // Add missing method from template
  trackBySessionId = (index: number, item: any) => item.id;

  /**
   * 渲染制品
   * 从ChatComponent.renderArtifact()方法抽取的逻辑
   */
  private renderArtifact(artifactId: string, versionId: string): void {
    // Add a placeholder message for the artifact
    // Feed the placeholder with the artifact data after it's fetched
    let message: ChatMessage = {
      role: 'bot',
      inlineData: {
        displayName: 'Loading artifact...',
        data: '',
        mimeType: 'image/png',
      },
      timestamp: new Date()
    };
    this.insertMessageBeforeLoadingMessage(message);

    const currentIndex = this.messages.length - 2;

    this.artifactService
      .getArtifactVersion(
        this.userId,
        this.appName,
        this.sessionId,
        artifactId,
        versionId,
      )
      .subscribe((res) => {
        const mimeType = res.inlineData.mimeType;
        const base64Data = this.fileProcessingService.formatBase64Data(res.inlineData.data, mimeType);
        const mediaType = getMediaTypeFromMimetype(mimeType);

        let inlineData = {
          displayName: this.fileProcessingService.createDefaultArtifactName(mimeType),
          data: base64Data,
          mimeType: mimeType,
          mediaType,
        };

        this.messages[currentIndex] = {
          role: 'bot',
          inlineData,
          timestamp: new Date()
        };

        // To trigger ngOnChanges in the artifact tab component
        this.artifacts = [
          ...this.artifacts,
          {
            id: artifactId,
            data: base64Data,
            mimeType,
            versionId,
            mediaType: getMediaTypeFromMimetype(mimeType),
          },
        ];

        this.changeDetectorRef.detectChanges();
      }, (error) => {
        this.errorHandlingService.handleArtifactError(error, {
          operation: 'Render Artifact',
          userMessage: '加载制品失败'
        });
      });
  }

  /**
   * 下载制品
   */
  downloadArtifact(artifact: any): void {
    this.downloadService.downloadBase64Data(
      artifact.data,
      artifact.mimeType,
      artifact.id,
    );
  }

  /**
   * 打开图片查看对话框
   */
  openViewImageDialog(imageData: string | null): void {
    const dialogRef = this.dialog.open(ViewImageDialogComponent, {
      maxWidth: '90vw',
      maxHeight: '90vh',
      data: {
        imageData,
      },
    });
  }

  /**
   * 处理OAuth流程
   */
  private handleOAuthFlow(oauthEvent: LongRunningEvent): void {
    this.longRunningEventsService.updateEventStatus(oauthEvent.id, 'running');
    
    this.oauthHandlingService.handleLongRunningToolOAuth(
      [oauthEvent],
      this.appName,
      this.userId,
      this.sessionId,
      this.functionCallEventId,
      (responses) => {
        this.longRunningEventsService.removeFinishedEvents([oauthEvent]);
        this.processOAuthResponse(responses);
      },
      (error) => {
        this.longRunningEventsService.updateEventStatus(oauthEvent.id, 'failed');
        this.errorHandlingService.handleOAuthError(error, {
          operation: 'Handle OAuth Flow',
          userMessage: 'OAuth认证失败，请重试'
        });
      }
    );
  }

  /**
   * 处理OAuth响应
   */
  private processOAuthResponse(responses: any[]): void {
    let index = this.messages.length - 1;
    for (const e of responses) {
      if (e.content) {
        for (let part of e.content.parts) {
          index += 1;
          this.processPart(part, e);
        }
      }
    }
    this.changeDetectorRef.detectChanges();
  }

  /**
   * 打开长时间运行事件对话框
   */
  openLongRunningEventDialog(): void {
    if (this.longRunningEvents.length === 0) return;

    const dialogRef = this.dialog.open(PendingEventDialogComponent, {
      width: '600px',
      data: {
        event: this.longRunningEvents[0],
        appName: this.appName,
        userId: this.userId,
        sessionId: this.sessionId,
        functionCallEventId: this.functionCallEventId,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.longRunningEventsService.removeFinishedEvents(result.events);
        this.processOAuthResponse(result.response);
      }
    });
  }

  /**
   * 检查是否有待处理的长时间运行事件
   */
  hasPendingLongRunningEvents(): boolean {
    return this.longRunningEvents.length > 0;
  }

  /**
   * 切换工具调用详情的展开/折叠状态
   */
  toggleFunctionDetails(message: ChatMessage, type: 'call' | 'response'): void {
    if (type === 'call') {
      message.showCallDetails = !message.showCallDetails;
    } else {
      message.showResponseDetails = !message.showResponseDetails;
    }
  }
}