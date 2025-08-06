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
import { Observable } from 'rxjs';
import { AgentService } from './agent.service';
import { AgentRunRequest } from '../models/AgentRunRequest';
import { URLUtil } from '../../../utils/url-util';

@Injectable({
  providedIn: 'root'
})
export class OAuthHandlingService {
  private redirectUri = URLUtil.getBaseUrlWithoutPath();

  constructor(private agentService: AgentService) {}

  /**
   * 打开OAuth弹窗并处理认证流程
   * 从ChatComponent.openOAuthPopup()方法抽取的逻辑
   */
  openOAuthPopup(url: string): Promise<string> {
    return new Promise((resolve, reject) => {
      // Open OAuth popup
      const popup = window.open(url, 'oauthPopup', 'width=600,height=700');

      if (!popup) {
        reject('Popup blocked!');
        return;
      }

      // Listen for messages from the popup
      const listener = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) {
          return;  // Ignore messages from unknown sources
        }
        const { authResponseUrl } = event.data;
        if (authResponseUrl) {
          resolve(authResponseUrl);
          window.removeEventListener('message', listener);
        } else {
          console.log('OAuth failed', event);
        }
      };

      window.addEventListener('message', listener);

      // Clean up listener if popup is closed manually
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          window.removeEventListener('message', listener);
          reject('Popup was closed by user');
        }
      }, 1000);
    });
  }

  /**
   * 发送OAuth响应到服务器
   * 从ChatComponent.sendOAuthResponse()方法抽取的逻辑
   */
  sendOAuthResponse(
    func: any,
    authResponseUrl: string,
    appName: string,
    userId: string,
    sessionId: string,
    functionCallEventId: string
  ): Observable<string> {
    const authResponse: AgentRunRequest = {
      appName: appName,
      userId: userId,
      sessionId: sessionId,
      newMessage: {
        'role': 'user',
        'parts': [],
      },
    };

    var authConfig = structuredClone(func.args.authConfig);
    authConfig.exchangedAuthCredential.oauth2.authResponseUri = authResponseUrl;
    authConfig.exchangedAuthCredential.oauth2.redirectUri = this.redirectUri;

    authResponse.functionCallEventId = functionCallEventId;
    authResponse.newMessage.parts.push({
      'function_response': {
        id: func.id,
        name: func.name,
        response: authConfig,
      },
    });

    return this.agentService.runSse(authResponse);
  }

  /**
   * 更新重定向URI
   * 从ChatComponent.updateRedirectUri()方法抽取的逻辑
   */
  updateRedirectUri(urlString: string, newRedirectUri: string): string {
    try {
      const url = new URL(urlString);
      const searchParams = url.searchParams;
      searchParams.set('redirect_uri', newRedirectUri);
      return url.toString();
    } catch (error) {
      console.warn('Failed to update redirect URI: ', error);
      return urlString;
    }
  }

  /**
   * 处理长时间运行的工具使用中的OAuth流程
   */
  handleLongRunningToolOAuth(
    longRunningEvents: any[],
    appName: string,
    userId: string,
    sessionId: string,
    functionCallEventId: string,
    onOAuthComplete: (response: any[]) => void,
    onOAuthError: (error: any) => void
  ): void {
    const func = longRunningEvents[0];
    
    if (func.args.authConfig &&
        func.args.authConfig.exchangedAuthCredential &&
        func.args.authConfig.exchangedAuthCredential.oauth2) {
      // for OAuth
      const authUri = func.args.authConfig.exchangedAuthCredential.oauth2.authUri;
      const updatedAuthUri = this.updateRedirectUri(authUri, this.redirectUri);
      
      this.openOAuthPopup(updatedAuthUri)
        .then((authResponseUrl) => {
          const responses: any[] = [];
          
          this.sendOAuthResponse(
            func, 
            authResponseUrl, 
            appName, 
            userId, 
            sessionId, 
            functionCallEventId
          ).subscribe({
            next: (chunk) => {
              try {
                const chunkJson = JSON.parse(chunk);
                responses.push(chunkJson);
              } catch (error) {
                console.error('Error parsing OAuth response chunk:', error);
              }
            },
            error: (err) => {
              console.error('OAuth SSE error:', err);
              onOAuthError(err);
            },
            complete: () => {
              onOAuthComplete(responses);
            }
          });
        })
        .catch((error) => {
          console.error('OAuth Error:', error);
          onOAuthError(error);
        });
    }
  }

  /**
   * 获取当前重定向URI
   */
  getRedirectUri(): string {
    return this.redirectUri;
  }
}