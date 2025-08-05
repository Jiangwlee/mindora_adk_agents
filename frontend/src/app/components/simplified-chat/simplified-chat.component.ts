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

export interface ChatMessage {
  role: 'user' | 'bot';
  text?: string;
  isLoading?: boolean;
  attachments?: {file: File; url: string}[];
  inlineData?: {
    displayName: string;
    data: string;
    mimeType: string;
    mediaType?: MediaType;
  };
  functionCall?: any;
  functionResponse?: any;
  thought?: boolean;
  timestamp?: Date;
}

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
  selectedFiles: {file: File; url: string}[] = [];
  isLoading = false;
  
  private streamingTextMessage: ChatMessage | null = null;
  private readonly messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  private readonly scrollInterruptedSubject = new BehaviorSubject(true);
  private readonly isModelThinkingSubject = new BehaviorSubject(false);
  
  private readonly snackBar = inject(MatSnackBar);
  private readonly changeDetectorRef = inject(ChangeDetectorRef);

  constructor(
    private agentService: AgentService,
    private sessionService: SessionService,
    private destroyRef: DestroyRef
  ) {}

  ngOnInit(): void {
    this.setupMessageHandling();
    this.loadSessionMessages();
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

  private loadSessionMessages(): void {
    if (!this.sessionId || !this.appName || !this.userId) return;

    this.sessionService.getSession(this.userId, this.appName, this.sessionId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (session) => {
          if (session?.events) {
            this.messages = this.transformSessionEvents(session.events);
            this.messagesSubject.next(this.messages);
            this.messageCountChanged.emit(this.messages.length);
          }
        },
        error: (err) => {
          console.error('Error loading session messages:', err);
        }
      });
  }

  private transformSessionEvents(events: any[]): ChatMessage[] {
    const messages: ChatMessage[] = [];
    
    events.forEach(event => {
      if (event.content?.parts) {
        // Group parts by type to avoid duplicating text messages
        const textParts: any[] = [];
        const otherParts: any[] = [];
        
        event.content.parts.forEach((part: any) => {
          if (part.text) {
            textParts.push(part);
          } else {
            otherParts.push(part);
          }
        });
        
        // Combine all text parts into a single message
        if (textParts.length > 0) {
          const combinedText = textParts.map(part => part.text).join('');
          const isThought = textParts.some(part => part.thought);
          
          const textMessage: ChatMessage = {
            role: event.author === 'user' ? 'user' : 'bot',
            text: combinedText,
            thought: isThought,
            timestamp: new Date(event.timestamp || Date.now())
          };
          messages.push(textMessage);
        }
        
        // Handle other parts separately
        otherParts.forEach((part: any) => {
          const message: ChatMessage = {
            role: event.author === 'user' ? 'user' : 'bot',
            timestamp: new Date(event.timestamp || Date.now())
          };

          if (part.functionCall) {
            message.functionCall = part.functionCall;
          } else if (part.functionResponse) {
            message.functionResponse = part.functionResponse;
          } else if (part.inlineData) {
            message.inlineData = {
              displayName: part.inlineData.displayName,
              data: this.formatBase64Data(part.inlineData.data, part.inlineData.mimeType),
              mimeType: part.inlineData.mimeType,
              mediaType: getMediaTypeFromMimetype(part.inlineData.mimeType)
            };
          }

          messages.push(message);
        });
      }
    });

    return messages;
  }

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
        parts: await this.getUserMessageParts()
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
          console.error('SSE error:', err);
          this.snackBar.open('发送消息失败，请重试', '确定');
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
      this.snackBar.open(chunk, '确定');
      return;
    }

    try {
      const chunkJson = JSON.parse(chunk);
      
      if (chunkJson.error) {
        this.snackBar.open(chunkJson.error, '确定');
        return;
      }

      if (chunkJson.content?.parts) {
        for (const part of chunkJson.content.parts) {
          this.processPart(part, chunkJson);
        }
      }

      this.changeDetectorRef.detectChanges();
    } catch (error) {
      console.error('Error parsing stream chunk:', error);
    }
  }

  private processPart(part: any, chunkJson: any): void {
    if (part.text) {
      this.isModelThinkingSubject.next(false);
      
      if (part.thought) {
        // Handle thought messages separately
        const thoughtMessage: ChatMessage = {
          role: 'bot',
          text: part.text,
          thought: true,
          timestamp: new Date()
        };
        this.insertMessageBeforeLoadingMessage(thoughtMessage);
      } else if (chunkJson.partial === true) {
        // Handle partial streaming messages - update existing or create new
        if (!this.streamingTextMessage) {
          this.streamingTextMessage = {
            role: 'bot',
            text: part.text,
            timestamp: new Date()
          };
          this.insertMessageBeforeLoadingMessage(this.streamingTextMessage);
        } else {
          // For partial messages, append incrementally
          this.streamingTextMessage.text = (this.streamingTextMessage.text || '') + part.text;
        }
      } else {
        // Handle final/complete messages - replace streaming message with final
        if (this.streamingTextMessage) {
          this.streamingTextMessage.text = part.text;
        } else {
          const finalMessage: ChatMessage = {
            role: 'bot',
            text: part.text,
            timestamp: new Date()
          };
          this.insertMessageBeforeLoadingMessage(finalMessage);
        }
      }
    } else if (part.functionCall) {
      const functionMessage: ChatMessage = {
        role: 'bot',
        functionCall: part.functionCall,
        timestamp: new Date()
      };
      this.insertMessageBeforeLoadingMessage(functionMessage);
    } else if (part.functionResponse) {
      const functionResponseMessage: ChatMessage = {
        role: 'bot',
        functionResponse: part.functionResponse,
        timestamp: new Date()
      };
      this.insertMessageBeforeLoadingMessage(functionResponseMessage);
    } else if (part.inlineData) {
      const inlineDataMessage: ChatMessage = {
        role: 'bot',
        inlineData: {
          displayName: part.inlineData.displayName,
          data: this.formatBase64Data(part.inlineData.data, part.inlineData.mimeType),
          mimeType: part.inlineData.mimeType,
          mediaType: getMediaTypeFromMimetype(part.inlineData.mimeType)
        },
        timestamp: new Date()
      };
      this.insertMessageBeforeLoadingMessage(inlineDataMessage);
    }
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

  private async getUserMessageParts(): Promise<any[]> {
    const parts: any[] = [];

    if (this.userInput.trim()) {
      parts.push({text: this.userInput});
    }

    if (this.selectedFiles.length > 0) {
      for (const file of this.selectedFiles) {
        parts.push({
          inlineData: {
            displayName: file.file.name,
            data: await this.readFileAsBytes(file.file),
            mimeType: file.file.type
          }
        });
      }
    }

    return parts;
  }

  private readFileAsBytes(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        const base64Data = e.target.result.split(',')[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  private formatBase64Data(data: string, mimeType: string): string {
    return `data:${mimeType};base64,${data}`;
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      for (let i = 0; i < input.files.length; i++) {
        const file = input.files[i];
        const url = URL.createObjectURL(file);
        this.selectedFiles.push({file, url});
      }
    }
    input.value = '';
  }

  removeFile(index: number): void {
    URL.revokeObjectURL(this.selectedFiles[index].url);
    this.selectedFiles.splice(index, 1);
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
}