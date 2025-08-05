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
import {MatDialog} from '@angular/material/dialog';
import {of} from 'rxjs';

import {ChatHistorySidebarComponent} from './chat-history-sidebar.component';
import {SessionService} from '../../core/services/session.service';

describe('ChatHistorySidebarComponent', () => {
  let component: ChatHistorySidebarComponent;
  let fixture: ComponentFixture<ChatHistorySidebarComponent>;
  let mockSessionService: jasmine.SpyObj<SessionService>;
  let mockDialog: jasmine.SpyObj<MatDialog>;

  beforeEach(async () => {
    const sessionServiceSpy = jasmine.createSpyObj('SessionService', ['listSessions', 'deleteSession']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);

    await TestBed.configureTestingModule({
      imports: [
        ChatHistorySidebarComponent,
        NoopAnimationsModule,
        HttpClientTestingModule
      ],
      providers: [
        {provide: SessionService, useValue: sessionServiceSpy},
        {provide: MatDialog, useValue: dialogSpy}
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatHistorySidebarComponent);
    component = fixture.componentInstance;
    mockSessionService = TestBed.inject(SessionService) as jasmine.SpyObj<SessionService>;
    mockDialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;

    // Setup default inputs
    component.appName = 'test-app';
    component.userId = 'test-user';
    component.currentSessionId = 'test-session-1';
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load sessions on init', () => {
    const mockSessions = {
      sessions: [
        {
          id: 'session-1',
          title: 'Test Session',
          createdAt: '2025-01-01T00:00:00Z',
          events: []
        }
      ]
    };

    mockSessionService.listSessions.and.returnValue(of(mockSessions));

    component.ngOnInit();

    expect(mockSessionService.listSessions).toHaveBeenCalledWith('test-user', 'test-app');
    expect(component.sessions.length).toBe(1);
  });

  it('should emit session selected event', () => {
    spyOn(component.sessionSelected, 'emit');

    component.onSessionClick('new-session-id');

    expect(component.sessionSelected.emit).toHaveBeenCalledWith('new-session-id');
  });

  it('should emit new session requested event', () => {
    spyOn(component.newSessionRequested, 'emit');

    component.onNewSession();

    expect(component.newSessionRequested.emit).toHaveBeenCalled();
  });

  it('should format timestamp correctly', () => {
    const now = new Date();
    const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);
    const twoDaysAgo = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);

    expect(component.formatTimestamp(thirtyMinutesAgo)).toBe('30分钟前');
    expect(component.formatTimestamp(twoDaysAgo)).toBe('2天前');
  });
});