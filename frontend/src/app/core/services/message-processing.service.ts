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

import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { getMediaTypeFromMimetype, MediaType } from '../../components/artifact-tab/artifact-tab.component';

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
  eventId?: string;
  renderedContent?: string;
  evalStatus?: any;
  failedMetric?: any;
  evalScore?: any;
  evalThreshold?: any;
  actualInvocationToolUses?: any;
  expectedInvocationToolUses?: any;
  actualFinalResponse?: any;
  expectedFinalResponse?: any;
  invocationIndex?: number;
  finalResponsePartIndex?: number;
  toolUseIndex?: number;
  showCallDetails?: boolean;
  showResponseDetails?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class MessageProcessingService {
  private readonly isModelThinkingSubject = new BehaviorSubject(false);
  
  constructor() {}

  /**
   * 处理SSE流响应中的单个part
   * 这是从ChatComponent.processPart()方法抽取的核心逻辑
   */
  processPart(
    part: any, 
    chunkJson: any, 
    streamingTextMessage: ChatMessage | null,
    messages: ChatMessage[],
    insertMessageCallback: (message: ChatMessage) => void
  ): { 
    streamingTextMessage: ChatMessage | null, 
    latestThought: string,
    isModelThinking: boolean 
  } {
    let latestThought = '';
    let isModelThinking = false;

    const renderedContent = chunkJson.groundingMetadata?.searchEntryPoint?.renderedContent;

    if (part.text) {
      this.isModelThinkingSubject.next(false);
      
      if (part.thought) {
        // Handle thought messages separately
        const thoughtMessage: ChatMessage = {
          role: 'bot',
          text: this.processThoughtText(part.text.trimEnd()),
          thought: true,
          timestamp: new Date(),
          eventId: chunkJson.id
        };
        insertMessageCallback(thoughtMessage);
        latestThought = part.text;
      } else if (chunkJson.partial === true) {
        // Handle partial streaming messages - update existing or create new
        if (!streamingTextMessage) {
          streamingTextMessage = {
            role: 'bot',
            text: part.text,
            timestamp: new Date(),
            eventId: chunkJson.id
          };
          
          if (renderedContent) {
            streamingTextMessage.renderedContent = renderedContent;
          }
          
          insertMessageCallback(streamingTextMessage);
        } else {
          // For partial messages, append incrementally
          streamingTextMessage.text = (streamingTextMessage.text || '') + part.text;
        }
      } else {
        // Handle final/complete messages - replace streaming message with final
        if (streamingTextMessage) {
          streamingTextMessage.text = part.text.trimEnd();
        } else {
          const finalMessage: ChatMessage = {
            role: 'bot',
            text: part.text.trimEnd(),
            timestamp: new Date(),
            eventId: chunkJson.id
          };
          
          if (renderedContent) {
            finalMessage.renderedContent = renderedContent;
          }
          
          insertMessageCallback(finalMessage);
        }
      }
    } else if (part.functionCall) {
      const functionMessage: ChatMessage = {
        role: 'bot',
        functionCall: part.functionCall,
        timestamp: new Date(),
        eventId: chunkJson.id
      };
      insertMessageCallback(functionMessage);
    } else if (part.functionResponse) {
      const functionResponseMessage: ChatMessage = {
        role: 'bot',
        functionResponse: part.functionResponse,
        timestamp: new Date(),
        eventId: chunkJson.id
      };
      insertMessageCallback(functionResponseMessage);
    } else if (part.inlineData) {
      const inlineDataMessage: ChatMessage = {
        role: 'bot',
        inlineData: {
          displayName: part.inlineData.displayName,
          data: this.formatBase64Data(part.inlineData.data, part.inlineData.mimeType),
          mimeType: part.inlineData.mimeType,
          mediaType: getMediaTypeFromMimetype(part.inlineData.mimeType)
        },
        timestamp: new Date(),
        eventId: chunkJson.id
      };
      insertMessageCallback(inlineDataMessage);
    } else if (part.executableCode) {
      const executableCodeMessage: ChatMessage = {
        role: 'bot',
        functionCall: { name: 'code_execution', args: { code: part.executableCode.code } },
        timestamp: new Date(),
        eventId: chunkJson.id
      };
      insertMessageCallback(executableCodeMessage);
    } else if (part.codeExecutionResult) {
      const codeResultMessage: ChatMessage = {
        role: 'bot',
        functionResponse: { 
          name: 'code_execution', 
          response: { 
            outcome: part.codeExecutionResult.outcome,
            output: part.codeExecutionResult.output 
          }
        },
        timestamp: new Date(),
        eventId: chunkJson.id
      };
      insertMessageCallback(codeResultMessage);
    } else if (part.thought) {
      isModelThinking = true;
      this.isModelThinkingSubject.next(true);
    }

    return { 
      streamingTextMessage, 
      latestThought,
      isModelThinking 
    };
  }

  /**
   * 转换会话事件为ChatMessage数组
   * 这是从SimplifiedChatComponent.transformSessionEvents()方法抽取的逻辑
   */
  transformSessionEvents(events: any[]): ChatMessage[] {
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
            timestamp: new Date(event.timestamp || Date.now()),
            eventId: event.id
          };
          messages.push(textMessage);
        }
        
        // Handle other parts separately
        otherParts.forEach((part: any) => {
          const message: ChatMessage = {
            role: event.author === 'user' ? 'user' : 'bot',
            timestamp: new Date(event.timestamp || Date.now()),
            eventId: event.id
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

  /**
   * 格式化Base64数据为完整的data URL
   */
  private formatBase64Data(data: string, mimeType: string): string {
    return `data:${mimeType};base64,${data}`;
  }

  /**
   * 处理思考文本，移除特殊标记
   */
  private processThoughtText(text: string): string {
    return text.replace('/*PLANNING*/', '').replace('/*ACTION*/', '');
  }

  /**
   * 获取模型思考状态的Observable
   */
  getModelThinkingState() {
    return this.isModelThinkingSubject.asObservable();
  }
}