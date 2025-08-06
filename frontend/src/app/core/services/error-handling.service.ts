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
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';

export interface ErrorContext {
  operation?: string;
  userMessage?: string;
  logLevel?: 'error' | 'warn' | 'info';
  showSnackBar?: boolean;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ErrorHandlingService {

  constructor(private snackBar: MatSnackBar) {}

  /**
   * 处理HTTP错误
   */
  handleHttpError(error: HttpErrorResponse, context: ErrorContext = {}): Observable<never> {
    const defaultContext: ErrorContext = {
      operation: 'HTTP Request',
      logLevel: 'error',
      showSnackBar: true,
      duration: 5000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    let userMessage = finalContext.userMessage || this.getDefaultErrorMessage(error);
    
    // Log the error
    this.logError(error, finalContext);
    
    // Show user-friendly message
    if (finalContext.showSnackBar) {
      this.showErrorMessage(userMessage, finalContext.duration);
    }
    
    return throwError(() => error);
  }

  /**
   * 处理SSE流错误
   */
  handleStreamError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'SSE Stream',
      userMessage: '流式响应出错，请重试',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 处理会话相关错误
   */
  handleSessionError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'Session Management',
      userMessage: '会话操作失败，请重试',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 处理文件上传错误
   */
  handleFileUploadError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'File Upload',
      userMessage: '文件上传失败，请检查文件格式和大小',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 处理OAuth错误
   */
  handleOAuthError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'OAuth Authentication',
      userMessage: 'OAuth认证失败，请重试',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 处理制品相关错误
   */
  handleArtifactError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'Artifact Processing',
      userMessage: '制品处理失败，请重试',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 处理一般性错误
   */
  handleGenericError(error: any, context: ErrorContext = {}): void {
    const defaultContext: ErrorContext = {
      operation: 'Generic Operation',
      userMessage: '操作失败，请重试',
      logLevel: 'error',
      showSnackBar: true,
      duration: 3000
    };
    
    const finalContext = { ...defaultContext, ...context };
    
    this.logError(error, finalContext);
    
    if (finalContext.showSnackBar) {
      this.showErrorMessage(finalContext.userMessage!, finalContext.duration);
    }
  }

  /**
   * 显示成功消息
   */
  showSuccessMessage(message: string, duration: number = 2000): void {
    this.snackBar.open(message, '确定', {
      duration,
      panelClass: ['success-snackbar']
    });
  }

  /**
   * 显示警告消息
   */
  showWarningMessage(message: string, duration: number = 3000): void {
    this.snackBar.open(message, '确定', {
      duration,
      panelClass: ['warning-snackbar']
    });
  }

  /**
   * 显示信息消息
   */
  showInfoMessage(message: string, duration: number = 2000): void {
    this.snackBar.open(message, '确定', {
      duration,
      panelClass: ['info-snackbar']
    });
  }

  /**
   * 显示错误消息
   */
  private showErrorMessage(message: string, duration: number = 3000): void {
    this.snackBar.open(message, '确定', {
      duration,
      panelClass: ['error-snackbar']
    });
  }

  /**
   * 记录错误
   */
  private logError(error: any, context: ErrorContext): void {
    const logMessage = `[${context.operation}] Error: ${error.message || error}`;
    
    switch (context.logLevel) {
      case 'warn':
        console.warn(logMessage, error);
        break;
      case 'info':
        console.info(logMessage, error);
        break;
      case 'error':
      default:
        console.error(logMessage, error);
        break;
    }
  }

  /**
   * 获取默认错误消息
   */
  private getDefaultErrorMessage(error: HttpErrorResponse): string {
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      return `网络错误: ${error.error.message}`;
    } else {
      // Server-side error
      switch (error.status) {
        case 400:
          return '请求参数错误';
        case 401:
          return '未授权，请重新登录';
        case 403:
          return '访问被拒绝';
        case 404:
          return '请求的资源不存在';
        case 500:
          return '服务器内部错误';
        case 502:
          return '网关错误';
        case 503:
          return '服务暂时不可用';
        default:
          return `服务器错误 (${error.status}): ${error.message}`;
      }
    }
  }
}