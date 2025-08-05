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

import {ComponentFixture, TestBed} from '@angular/core/testing';
import {NoopAnimationsModule} from '@angular/platform-browser/animations';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {of} from 'rxjs';

import {SimplifiedChatComponent} from './simplified-chat.component';
import {AgentService} from '../../core/services/agent.service';
import {SessionService} from '../../core/services/session.service';

describe('SimplifiedChatComponent', () => {
  let component: SimplifiedChatComponent;
  let fixture: ComponentFixture<SimplifiedChatComponent>;
  let mockAgentService: jasmine.SpyObj<AgentService>;
  let mockSessionService: jasmine.SpyObj<SessionService>;

  beforeEach(async () => {
    const agentServiceSpy = jasmine.createSpyObj('AgentService', ['runSse', 'getLoadingState']);
    const sessionServiceSpy = jasmine.createSpyObj('SessionService', ['getSession']);

    await TestBed.configureTestingModule({
      imports: [
        SimplifiedChatComponent,
        NoopAnimationsModule,
        HttpClientTestingModule,
        MatSnackBarModule
      ],
      providers: [
        {provide: AgentService, useValue: agentServiceSpy},
        {provide: SessionService, useValue: sessionServiceSpy}
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SimplifiedChatComponent);
    component = fixture.componentInstance;
    mockAgentService = TestBed.inject(AgentService) as jasmine.SpyObj<AgentService>;
    mockSessionService = TestBed.inject(SessionService) as jasmine.SpyObj<SessionService>;

    // Setup default values
    component.appName = 'test-app';
    component.sessionId = 'test-session';
    component.userId = 'test-user';
    component.appDisplayName = 'Test App';
    component.appDescription = 'Test Description';

    // Setup default mocks
    mockAgentService.getLoadingState.and.returnValue(of(false));
    mockSessionService.getSession.and.returnValue(of({events: []}));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load session messages on init', () => {
    const mockSession = {
      events: [
        {
          author: 'user',
          content: {
            parts: [{text: 'Hello'}]
          },
          timestamp: '2025-01-01T00:00:00Z'
        }
      ]
    };

    mockSessionService.getSession.and.returnValue(of(mockSession));

    component.ngOnInit();

    expect(mockSessionService.getSession).toHaveBeenCalledWith('test-user', 'test-app', 'test-session');
    expect(component.messages.length).toBe(1);
    expect(component.messages[0].text).toBe('Hello');
  });

  it('should handle file selection', () => {
    const mockFile = new File(['test'], 'test.txt', {type: 'text/plain'});
    const mockEvent = {
      target: {
        files: [mockFile],
        value: ''
      }
    } as any;

    component.onFileSelect(mockEvent);

    expect(component.selectedFiles.length).toBe(1);
    expect(component.selectedFiles[0].file).toBe(mockFile);
  });

  it('should remove selected file', () => {
    const mockFile = new File(['test'], 'test.txt', {type: 'text/plain'});
    component.selectedFiles = [{
      file: mockFile,
      url: 'blob:test-url'
    }];

    spyOn(URL, 'revokeObjectURL');

    component.removeFile(0);

    expect(component.selectedFiles.length).toBe(0);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url');
  });

  it('should not send empty message', async () => {
    component.userInput = '';
    component.selectedFiles = [];

    await component.sendMessage();

    expect(mockAgentService.runSse).not.toHaveBeenCalled();
  });
});