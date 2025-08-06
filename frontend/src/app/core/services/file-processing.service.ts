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

export interface FileWithUrl {
  file: File;
  url: string;
}

@Injectable({
  providedIn: 'root'
})
export class FileProcessingService {
  
  constructor() {}

  /**
   * 将文件读取为Base64字符串
   * 这是从ChatComponent.readFileAsBytes()方法抽取的逻辑
   */
  readFileAsBytes(file: File): Promise<string> {
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

  /**
   * 构建用户消息的parts数组
   * 这是从ChatComponent.getUserMessageParts()方法抽取的逻辑
   */
  async getUserMessageParts(userInput: string, selectedFiles: FileWithUrl[]): Promise<any[]> {
    const parts: any[] = [];

    if (userInput.trim()) {
      parts.push({ text: userInput });
    }

    if (selectedFiles.length > 0) {
      for (const fileWithUrl of selectedFiles) {
        parts.push({
          inlineData: {
            displayName: fileWithUrl.file.name,
            data: await this.readFileAsBytes(fileWithUrl.file),
            mimeType: fileWithUrl.file.type
          }
        });
      }
    }

    return parts;
  }

  /**
   * 处理文件选择事件，创建FileWithUrl数组
   */
  handleFileSelection(event: Event, currentFiles: FileWithUrl[] = []): FileWithUrl[] {
    const input = event.target as HTMLInputElement;
    const newFiles: FileWithUrl[] = [...currentFiles];
    
    if (input.files) {
      for (let i = 0; i < input.files.length; i++) {
        const file = input.files[i];
        const url = URL.createObjectURL(file);
        newFiles.push({ file, url });
      }
    }
    
    // Clear the input value to allow selecting the same file again
    input.value = '';
    
    return newFiles;
  }

  /**
   * 移除指定索引的文件并清理URL
   */
  removeFile(files: FileWithUrl[], index: number): FileWithUrl[] {
    if (index >= 0 && index < files.length) {
      URL.revokeObjectURL(files[index].url);
      const newFiles = [...files];
      newFiles.splice(index, 1);
      return newFiles;
    }
    return files;
  }

  /**
   * 清理所有文件URL以防止内存泄漏
   */
  cleanupFileUrls(files: FileWithUrl[]): void {
    files.forEach(fileWithUrl => {
      URL.revokeObjectURL(fileWithUrl.url);
    });
  }

  /**
   * 修复Base64字符串格式
   * 这是从ChatComponent中的fixBase64String函数抽取的逻辑
   */
  fixBase64String(base64: string): string {
    // Replace URL-safe characters if they exist
    base64 = base64.replace(/-/g, '+').replace(/_/g, '/');

    // Fix base64 padding
    while (base64.length % 4 !== 0) {
      base64 += '=';
    }

    return base64;
  }

  /**
   * 格式化Base64数据为完整的data URL
   * 这是从ChatComponent.formatBase64Data()方法抽取的逻辑
   */
  formatBase64Data(data: string, mimeType: string): string {
    const fixedBase64Data = this.fixBase64String(data);
    return `data:${mimeType};base64,${fixedBase64Data}`;
  }

  /**
   * 根据MIME类型创建默认的制品名称
   */
  createDefaultArtifactName(mimeType: string): string {
    if (!mimeType || !mimeType.includes('/')) {
      return '';
    }
    return mimeType.replace('/', '.');
  }

  /**
   * 验证文件类型是否被支持
   */
  isFileTypeSupported(file: File): boolean {
    const supportedTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'text/plain',
      'application/pdf',
      'application/json',
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    return supportedTypes.includes(file.type) || file.type.startsWith('text/');
  }

  /**
   * 获取文件大小的可读格式
   */
  getHumanReadableFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}