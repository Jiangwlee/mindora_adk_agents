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

export interface LongRunningEvent {
  id: string;
  name: string;
  args: any;
  timestamp?: Date;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

@Injectable({
  providedIn: 'root'
})
export class LongRunningEventsService {
  private readonly longRunningEventsSubject = new BehaviorSubject<LongRunningEvent[]>([]);
  private longRunningEvents: LongRunningEvent[] = [];

  constructor() {}

  /**
   * 从parts中提取异步函数调用
   * 从ChatComponent.getAsyncFunctionsFromParts()方法抽取的逻辑
   */
  extractAsyncFunctionsFromParts(pendingIds: string[], parts: any[]): LongRunningEvent[] {
    const events: LongRunningEvent[] = [];
    
    for (const part of parts) {
      if (part.functionCall && pendingIds.includes(part.functionCall.id)) {
        const event: LongRunningEvent = {
          id: part.functionCall.id,
          name: part.functionCall.name,
          args: part.functionCall.args,
          timestamp: new Date(),
          status: 'pending'
        };
        events.push(event);
      }
    }
    
    return events;
  }

  /**
   * 添加长时间运行事件
   */
  addLongRunningEvents(events: LongRunningEvent[]): void {
    this.longRunningEvents.push(...events);
    this.longRunningEventsSubject.next([...this.longRunningEvents]);
  }

  /**
   * 移除已完成的长时间运行事件
   * 从ChatComponent.removeFinishedLongRunningEvents()方法抽取的逻辑
   */
  removeFinishedEvents(finishedEvents: any[]): void {
    const idsToExclude = new Set(finishedEvents.map((obj: any) => obj.id));
    this.longRunningEvents = this.longRunningEvents.filter(obj => !idsToExclude.has(obj.id));
    this.longRunningEventsSubject.next([...this.longRunningEvents]);
  }

  /**
   * 更新事件状态
   */
  updateEventStatus(eventId: string, status: LongRunningEvent['status']): void {
    const event = this.longRunningEvents.find(e => e.id === eventId);
    if (event) {
      event.status = status;
      this.longRunningEventsSubject.next([...this.longRunningEvents]);
    }
  }

  /**
   * 获取长时间运行事件的Observable
   */
  getLongRunningEvents() {
    return this.longRunningEventsSubject.asObservable();
  }

  /**
   * 获取当前的长时间运行事件列表
   */
  getCurrentEvents(): LongRunningEvent[] {
    return [...this.longRunningEvents];
  }

  /**
   * 清空所有长时间运行事件
   */
  clearAllEvents(): void {
    this.longRunningEvents = [];
    this.longRunningEventsSubject.next([]);
  }

  /**
   * 获取特定事件
   */
  getEvent(eventId: string): LongRunningEvent | undefined {
    return this.longRunningEvents.find(e => e.id === eventId);
  }

  /**
   * 检查是否有待处理的OAuth事件
   */
  hasPendingOAuthEvents(): boolean {
    return this.longRunningEvents.some(event => 
      event.status === 'pending' &&
      event.args?.authConfig?.exchangedAuthCredential?.oauth2
    );
  }

  /**
   * 获取第一个待处理的OAuth事件
   */
  getFirstPendingOAuthEvent(): LongRunningEvent | undefined {
    return this.longRunningEvents.find(event => 
      event.status === 'pending' &&
      event.args?.authConfig?.exchangedAuthCredential?.oauth2
    );
  }
}