# Next.js + FastAPI + Google ADK AI Agent Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Google ADK Architecture Analysis](#google-adk-architecture-analysis)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Strategy](#implementation-strategy)
5. [Backend Implementation (FastAPI + Google ADK)](#backend-implementation)
6. [Frontend Implementation (Next.js)](#frontend-implementation)
7. [Integration Patterns](#integration-patterns)
8. [Deployment Considerations](#deployment-considerations)
9. [Best Practices and Lessons Learned](#best-practices-and-lessons-learned)

## Overview

This document provides a comprehensive analysis of Google's Agent Development Kit (ADK) and outlines a complete implementation strategy for building an AI Agent application using Next.js as the frontend, FastAPI as the backend, and Google ADK as the agent framework.

### Key Components
- **Frontend**: Next.js with TypeScript, modern React patterns
- **Backend**: FastAPI with async/await patterns, WebSocket support
- **Agent Framework**: Google ADK with Vertex AI/Gemini integration
- **Communication**: Server-Sent Events (SSE) for streaming, WebSocket for real-time
- **State Management**: Session-based with event-driven architecture

## Google ADK Architecture Analysis

### Core ADK Components

#### 1. Agent Definition Pattern
Based on the analysis of sample agents, ADK agents follow a consistent pattern:

```python
# Basic Agent Structure
from google.adk.agents import Agent
from google.adk.tools import tool

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agent_name',
    instruction=system_prompt,
    tools=[tool1, tool2, ...],
    sub_agents=[sub_agent1, sub_agent2, ...],
    callbacks=[callback_function]
)
```

#### 2. Agent Types Available
- **LlmAgent**: Basic LLM-powered agent
- **SequentialAgent**: Executes sub-agents in sequence
- **LoopAgent**: Iterative execution with conditional termination
- **BaseAgent**: Custom agent implementation base class

#### 3. Tool Integration
Tools are Python functions decorated with ADK tool annotations:
```python
@tool
def custom_tool(input_param: str) -> str:
    """Tool description."""
    # Tool implementation
    return result
```

#### 4. Session Management
- Session-based conversation tracking
- Event-driven architecture with structured events
- State persistence across agent invocations
- Artifact management for files and generated content

### Communication Patterns

#### 1. Server-Sent Events (SSE)
Primary communication method for agent execution:
- Real-time streaming of agent responses
- Structured JSON event format
- Support for different content types (text, function calls, artifacts)

#### 2. WebSocket Integration
For bidirectional communication:
- Audio/video streaming support
- Real-time interaction capabilities
- Binary data handling

#### 3. REST API
For session management and agent listing:
- CRUD operations for sessions
- Agent discovery and configuration
- Evaluation and testing endpoints

### API Server Implementation Patterns

#### 1. FastAPI Backend Architecture
Based on the existing AI Agent Platform implementation, here's the recommended FastAPI structure:

**File Structure:**
```
backend/
├── main.py                 # Application entry point
├── api/                    # API routers
│   ├── agents.py          # Agent management endpoints
│   ├── sessions.py        # Session management
│   ├── registry.py        # Agent registry operations
│   └── events.py          # Event streaming (SSE)
├── core/                   # Core services
│   ├── config.py          # Configuration management
│   ├── agent_registry.py  # Agent discovery and registration
│   └── session_manager.py # Session lifecycle management
└── requirements.txt       # Dependencies
```

#### 2. Core Components

**Configuration Management:**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GOOGLE_",
        case_sensitive=True,
    )
    
    # ADK Configuration
    CLOUD_PROJECT: str = "my_project"
    CLOUD_LOCATION: str = "us-central1"
    GENAI_USE_VERTEXAI: str = "1"
    
    # Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Session Configuration
    SESSION_TIMEOUT: int = 3600
    REDIS_URL: str | None = None
```

**Agent Registry:**
```python
class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_scanner = AgentScanner()
    
    async def register_agent(self, agent_id: str, agent_path: str):
        """Register an ADK agent from file path."""
        agent_info = await self.agent_scanner.scan_agent(agent_path)
        self.agents[agent_id] = agent_info
    
    async def get_agent(self, agent_id: str) -> AgentInfo:
        """Get registered agent information."""
        return self.agents.get(agent_id)
    
    async def list_agents(self) -> List[AgentInfo]:
        """List all registered agents."""
        return list(self.agents.values())
```

**Session Manager:**
```python
class SessionManager:
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
    
    async def create_session(
        self, 
        user_id: str, 
        agent_app_id: str,
        interface_type: str = "chat"
    ) -> Session:
        """Create a new session."""
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            agent_app_id=agent_app_id,
            interface_type=interface_type,
            created_at=datetime.utcnow(),
            state={},
            events=[]
        )
        await self.storage.save_session(session)
        return session
    
    async def get_session(self, session_id: str) -> Session:
        """Retrieve session by ID."""
        return await self.storage.get_session(session_id)
    
    async def add_event(self, session_id: str, event: Dict):
        """Add event to session."""
        session = await self.get_session(session_id)
        session.events.append(event)
        await self.storage.save_session(session)
```

#### 3. API Endpoints Design

**Agent Management:**
```python
@router.get("/agents")
async def list_agents():
    """List all available agents."""
    agents = await registry.list_agents()
    return {"agents": agents}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent information."""
    agent = await registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    background_tasks: BackgroundTasks
):
    """Execute agent with streaming response."""
    agent = await registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return StreamingResponse(
        agent_stream_generator(agent, request),
        media_type="text/event-stream"
    )
```

**Session Management:**
```python
@router.post("/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new session."""
    session = await session_manager.create_session(
        user_id=request.user_id,
        agent_app_id=request.agent_app_id,
        interface_type=request.interface_type
    )
    return {"session": session}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": session}

@router.get("/sessions/{session_id}/events")
async def get_session_events(session_id: str):
    """Get session event history."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"events": session.events}
```

**Event Streaming (SSE):**
```python
async def agent_stream_generator(agent: AgentInfo, request: AgentRunRequest):
    """Generate SSE events for agent execution."""
    try:
        # Get session
        session = await session_manager.get_session(request.session_id)
        
        # Execute ADK agent
        async for event in agent.agent.run_async(session, request.message):
            event_data = {
                "type": "agent_event",
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": request.session_id,
                "agent_id": agent.id,
                "data": event
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            
            # Store event in session
            await session_manager.add_event(request.session_id, event_data)
            
    except Exception as e:
        error_event = {
            "type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": request.session_id,
            "data": {"message": str(e), "code": "AGENT_EXECUTION_ERROR"}
        }
        yield f"data: {json.dumps(error_event)}\n\n"

@router.get("/events/stream/{session_id}")
async def stream_events(session_id: str):
    """SSE endpoint for real-time events."""
    return StreamingResponse(
        event_generator(session_id),
        media_type="text/event-stream"
    )
```

#### 4. Data Models

**Request/Response Models:**
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class AgentRunRequest(BaseModel):
    agent_id: str
    session_id: str
    message: str
    interface_type: str = "chat"
    context: Optional[Dict[str, Any]] = None
    streaming: bool = True

class SessionCreateRequest(BaseModel):
    user_id: str
    agent_app_id: str
    interface_type: str = "chat"
    metadata: Optional[Dict[str, Any]] = None

class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    version: str
    capabilities: List[str]
    interface_types: List[str]
    model: str
    tools: List[str]
    sub_agents: List[str]

class Session(BaseModel):
    id: str
    user_id: str
    agent_app_id: str
    interface_type: str
    created_at: str
    updated_at: str
    state: Dict[str, Any]
    events: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
```

#### 5. Error Handling and Middleware

**Global Exception Handler:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for consistent error responses."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

**CORS Middleware:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Authentication Middleware:**
```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Authentication middleware for API endpoints."""
    # Skip authentication for health checks and agent listing
    if request.url.path in ["/health", "/agents"]:
        return await call_next(request)
    
    # Extract API key from headers
    api_key = request.headers.get("Authorization")
    if not api_key or not api_key.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Missing or invalid authorization header"}
        )
    
    # Validate API key
    token = api_key.split(" ")[1]
    if not await validate_api_key(token):
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid API key"}
        )
    
    return await call_next(request)
```

#### 6. WebSocket Support

**WebSocket Endpoint:**
```python
from fastapi import WebSocket

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time bidirectional communication."""
    await websocket.accept()
    
    try:
        # Add client to connection manager
        await connection_manager.connect(session_id, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message and broadcast response
            response = await process_websocket_message(session_id, message)
            await connection_manager.broadcast(session_id, response)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id, websocket)
    except Exception as e:
        await connection_manager.send_error(session_id, str(e))
```

**Connection Manager:**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Connect a new WebSocket client."""
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, session_id: str, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def broadcast(self, session_id: str, message: dict):
        """Broadcast message to all clients in a session."""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove failed connections
                    self.active_connections[session_id].remove(connection)
```

### Communication Patterns

#### 1. Server-Sent Events (SSE)
Primary communication method for agent execution:

**Event Format:**
```json
{
  "type": "agent_event",
  "timestamp": "2025-01-01T12:00:00Z",
  "session_id": "uuid",
  "agent_id": "rag_agent",
  "data": {
    "content": {
      "parts": [{"text": "Agent response"}]
    },
    "interface_type": "chat",
    "function_calls": [],
    "artifacts": []
  }
}
```

**Client Implementation (Next.js):**
```typescript
async function* createEventSource(url: string) {
  const response = await fetch(url, {
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    }
  });
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader?.read() || { done: true };
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data) {
          try {
            const event = JSON.parse(data);
            yield event;
          } catch (e) {
            console.error('Error parsing SSE event:', e);
          }
        }
      }
    }
  }
}
```

#### 2. WebSocket Communication
For bidirectional communication:

**Message Format:**
```json
{
  "type": "user_message",
  "timestamp": "2025-01-01T12:00:00Z",
  "session_id": "uuid",
  "data": {
    "content": "User message",
    "interface_type": "chat"
  }
}
```

**Audio Streaming Support:**
```typescript
// Audio data handling
interface AudioMessage {
  type: "audio_data";
  timestamp: string;
  session_id: string;
  data: {
    audio_data: string; // base64 encoded
    sample_rate: number;
    channels: number;
  };
}

// Process audio chunks
function processAudioChunk(base64Audio: string) {
  const binaryString = atob(base64Audio);
  const bytes = new Uint8Array(binaryString.length);
  
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  // Convert to Float32Array for audio playback
  const float32Array = new Float32Array(bytes.length / 2);
  for (let i = 0; i < float32Array.length; i++) {
    let int16 = bytes[i * 2] | (bytes[i * 2 + 1] << 8);
    if (int16 >= 32768) int16 -= 65536;
    float32Array[i] = int16 / 32768.0;
  }
  
  return float32Array;
}
```

#### 3. REST API Integration
For session management and agent operations:

**Session API:**
```typescript
// Session management
class SessionService {
  async createSession(userId: string, agentAppId: string): Promise<Session> {
    const response = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        agent_app_id: agentAppId,
        interface_type: 'chat'
      })
    });
    return response.json();
  }
  
  async getSession(sessionId: string): Promise<Session> {
    const response = await fetch(`/api/sessions/${sessionId}`);
    return response.json();
  }
  
  async deleteSession(sessionId: string): Promise<void> {
    await fetch(`/api/sessions/${sessionId}`, {
      method: 'DELETE'
    });
  }
}
```

**Agent API:**
```typescript
// Agent operations
class AgentService {
  async listAgents(): Promise<AgentInfo[]> {
    const response = await fetch('/api/agents');
    const data = await response.json();
    return data.agents;
  }
  
  async runAgent(
    agentId: string,
    sessionId: string,
    message: string,
    onEvent: (event: AgentEvent) => void
  ): Promise<void> {
    const eventSource = new EventSource(
      `/api/agents/${agentId}/run?session_id=${sessionId}&message=${encodeURIComponent(message)}`
    );
    
    eventSource.onmessage = (event) => {
      const agentEvent = JSON.parse(event.data);
      onEvent(agentEvent);
    };
    
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      eventSource.close();
    };
  }
}
```

## Proposed Architecture

### System Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   Google ADK    │
│   Frontend      │◄──►│   Backend       │◄──►│   Agents        │
│                 │    │                 │    │                 │
│ • Components    │    │ • REST API      │    │ • Agent Logic   │
│ • State Mgmt    │    │ • WebSocket     │    │ • Tools         │
│ • SSE Client    │    │ • ADK Interface │    │ • Sub-agents    │
│ • WebSocket     │    │ • Session Mgmt  │    │ • Callbacks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Vertex AI     │
                    │   / Gemini      │
                    │                 │
                    │ • LLM Models    │
                    │ • Embeddings    │
                    │ • RAG Engine    │
                    └─────────────────┘
```

### Key Design Decisions

#### 1. Frontend Architecture (Next.js)
- **Framework**: Next.js 14+ with App Router
- **State Management**: React Context + useReducer for complex state
- **Real-time Communication**: Native EventSource for SSE, WebSocket API
- **UI Components**: Headless UI or shadcn/ui for consistent design
- **Type Safety**: Full TypeScript implementation

#### 2. Backend Architecture (FastAPI)
- **Framework**: FastAPI with async/await
- **ADK Integration**: Direct ADK library usage
- **Session Management**: Redis or in-memory session storage
- **Streaming**: SSE endpoint for agent execution
- **WebSocket**: Separate endpoint for real-time features

#### 3. Agent Layer Architecture
- **Agent Registry**: Dynamic agent discovery and loading
- **Tool System**: Extensible tool framework
- **Session Handling**: ADK session integration
- **Event Processing**: Structured event handling and forwarding

## Implementation Strategy

### Phase 1: Backend Foundation

#### 1.1 FastAPI Backend Setup
```python
# main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Agent Platform")

# CORS configuration for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router, prefix="/api/v1")
app.include_router(session_router, prefix="/api/v1")
```

#### 1.2 ADK Integration Layer
```python
# services/adk_service.py
from google.adk.sessions import Session
from google.adk.agents import Agent
from google.adk.events import Event
from typing import AsyncGenerator

class ADKService:
    def __init__(self):
        self.agents = self._load_agents()
    
    async def run_agent(
        self, 
        agent_name: str, 
        session_id: str, 
        message: dict
    ) -> AsyncGenerator[Event, None]:
        """Execute agent and stream events"""
        agent = self.agents[agent_name]
        session = await self._get_session(session_id)
        
        async for event in agent.run_async(session, message):
            yield event
    
    def _load_agents(self) -> dict[str, Agent]:
        """Load available agents"""
        agents = {}
        # Dynamic agent loading logic
        return agents
```

#### 1.3 Session Management
```python
# services/session_service.py
from typing import Dict, Optional
import uuid
import json

class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    async def create_session(self, user_id: str, app_name: str) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            user_id=user_id,
            app_name=app_name,
            state={}
        )
        self.sessions[session_id] = session
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID"""
        return self.sessions.get(session_id)
```

### Phase 2: Frontend Implementation

#### 2.1 Next.js Application Structure
```
src/
├── app/
│   ├── (app)/
│   │   ├── chat/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── agents/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   └── layout.tsx
│   ├── api/
│   │   └── [...nextauth]/route.ts
│   └── layout.tsx
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── Message.tsx
│   │   └── TypingIndicator.tsx
│   ├── agents/
│   │   ├── AgentCard.tsx
│   │   └── AgentList.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useAgents.ts
│   └── useWebSocket.ts
├── services/
│   ├── agentService.ts
│   ├── sessionService.ts
│   └── websocketService.ts
└── types/
    ├── agent.ts
    ├── session.ts
    └── event.ts
```

#### 2.2 Core Chat Component
```typescript
// components/chat/ChatInterface.tsx
'use client'

import { useState, useRef, useEffect } from 'react'
import { useChat } from '@/hooks/useChat'
import { Message } from './Message'
import { TypingIndicator } from './TypingIndicator'

export function ChatInterface() {
  const [input, setInput] = useState('')
  const [selectedAgent, setSelectedAgent] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const {
    messages,
    isLoading,
    sendMessage,
    agents,
    session
  } = useChat(selectedAgent)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    
    await sendMessage(input)
    setInput('')
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Agent Selection */}
      <div className="p-4 border-b">
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="">Select an agent...</option>
          {agents.map(agent => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded"
            disabled={isLoading || !selectedAgent}
          />
          <button
            type="submit"
            disabled={isLoading || !selectedAgent}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}
```

#### 2.3 Chat Hook Implementation
```typescript
// hooks/useChat.ts
'use client'

import { useState, useEffect, useCallback } from 'react'
import { EventSourcePolyfill } from 'event-source-polyfill'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: any
}

interface Agent {
  id: string
  name: string
  description: string
}

export function useChat(agentId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState<Agent[]>([])
  const [session, setSession] = useState<string | null>(null)

  // Load available agents
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await fetch('/api/v1/agents')
        const data = await response.json()
        setAgents(data.agents)
      } catch (error) {
        console.error('Failed to load agents:', error)
      }
    }
    
    loadAgents()
  }, [])

  // Create or load session
  useEffect(() => {
    if (agentId) {
      const createSession = async () => {
        try {
          const response = await fetch('/api/v1/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              user_id: 'user', 
              app_name: agentId 
            })
          })
          const data = await response.json()
          setSession(data.session_id)
        } catch (error) {
          console.error('Failed to create session:', error)
        }
      }
      
      createSession()
    }
  }, [agentId])

  const sendMessage = useCallback(async (content: string) => {
    if (!session || !agentId) return

    setIsLoading(true)
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    try {
      // Create SSE connection
      const eventSource = new EventSourcePolyfill(
        `/api/v1/run_sse?agent_name=${agentId}&session_id=${session}`,
        { headers: { 'Accept': 'text/event-stream' } }
      )

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.content) {
          const assistantMessage: Message = {
            id: data.id || Date.now().toString(),
            role: 'assistant',
            content: data.content.parts?.[0]?.text || '',
            timestamp: new Date(),
            metadata: data
          }
          
          setMessages(prev => [...prev, assistantMessage])
        }
        
        if (data.status === 'complete') {
          eventSource.close()
          setIsLoading(false)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        eventSource.close()
        setIsLoading(false)
      }

      // Send message via POST
      await fetch('/api/v1/run_sse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: agentId,
          session_id: session,
          new_message: {
            role: 'user',
            parts: [{ text: content }]
          }
        })
      })

    } catch (error) {
      console.error('Failed to send message:', error)
      setIsLoading(false)
    }
  }, [session, agentId])

  return {
    messages,
    isLoading,
    sendMessage,
    agents,
    session
  }
}
```

### Phase 3: Advanced Features

#### 3.1 WebSocket Service for Real-time Features
```typescript
// services/websocketService.ts
export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  connect(url: string, onMessage: (data: any) => void) {
    if (this.ws?.readyState === WebSocket.OPEN) return
    
    this.ws = new WebSocket(url)
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    this.ws.onclose = () => {
      this.handleReconnect(url, onMessage)
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  private handleReconnect(url: string, onMessage: (data: any) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        this.connect(url, onMessage)
      }, 1000 * Math.pow(2, this.reconnectAttempts))
    }
  }
  
  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
  
  disconnect() {
    this.ws?.close()
    this.ws = null
  }
}
```

#### 3.2 Agent Management System
```python
# services/agent_registry.py
from typing import Dict, List, Type
from google.adk.agents import Agent
import importlib
import os

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.agent_configs: Dict[str, dict] = {}
    
    def register_agent(self, name: str, agent: Agent, config: dict = None):
        """Register an agent with the system"""
        self.agents[name] = agent
        self.agent_configs[name] = config or {}
    
    def load_agents_from_directory(self, directory: str):
        """Dynamically load agents from a directory"""
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{directory}.{module_name}')
                    if hasattr(module, 'root_agent'):
                        agent_name = getattr(module, 'root_agent').name
                        self.register_agent(agent_name, getattr(module, 'root_agent'))
                except Exception as e:
                    print(f"Failed to load agent from {filename}: {e}")
    
    def get_agent(self, name: str) -> Agent:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[dict]:
        """List all available agents"""
        return [
            {
                'id': name,
                'name': agent.name,
                'description': getattr(agent, 'description', ''),
                'model': getattr(agent, 'model', 'unknown')
            }
            for name, agent in self.agents.items()
        ]
```

## Backend Implementation (FastAPI + Google ADK)

### Complete Backend Structure

```python
# backend/
├── main.py
├── api/
│   ├── __init__.py
│   ├── agents.py
│   ├── sessions.py
│   └── chat.py
├── services/
│   ├── __init__.py
│   ├── adk_service.py
│   ├── session_service.py
│   └── agent_registry.py
├── agents/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── rag_agent.py
│   └── custom/
│       ├── __init__.py
│       └── customer_service.py
├── tools/
│   ├── __init__.py
│   ├── search.py
│   └── calculator.py
├── models/
│   ├── __init__.py
│   ├── session.py
│   └── event.py
└── config/
    ├── __init__.py
    └── settings.py
```

### Main Application Entry Point

```python
# main.py
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from api import agents, sessions, chat
from services.agent_registry import AgentRegistry
from config.settings import settings

app = FastAPI(
    title="AI Agent Platform",
    description="Next.js + FastAPI + Google ADK Integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])

# Initialize agent registry
agent_registry = AgentRegistry()
agent_registry.load_agents_from_directory("agents")

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("Starting AI Agent Platform...")
    print(f"Loaded {len(agent_registry.list_agents())} agents")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents_loaded": len(agent_registry.list_agents())}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

### Configuration Management

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # Vertex AI settings
    VERTEX_AI_MODEL: str = "gemini-2.5-flash"
    
    # Session settings
    SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # Redis settings (optional)
    REDIS_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### API Endpoints Implementation

#### Agents API
```python
# api/agents.py
from fastapi import APIRouter, HTTPException
from typing import List

from services.agent_registry import agent_registry
from models.agent import AgentInfo

router = APIRouter()

@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    """List all available agents"""
    try:
        return agent_registry.list_agents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_name}", response_model=AgentInfo)
async def get_agent(agent_name: str):
    """Get specific agent information"""
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": agent_name,
        "name": agent.name,
        "description": getattr(agent, 'description', ''),
        "model": getattr(agent, 'model', 'unknown'),
        "tools": [tool.name for tool in getattr(agent, 'tools', [])]
    }
```

#### Sessions API
```python
# api/sessions.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from services.session_service import session_service
from models.session import Session, SessionCreate

router = APIRouter()

@router.post("/", response_model=Session)
async def create_session(session_data: SessionCreate):
    """Create a new session"""
    try:
        session_id = await session_service.create_session(
            user_id=session_data.user_id,
            app_name=session_data.app_name
        )
        session = await session_service.get_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session by ID"""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/", response_model=List[Session])
async def list_sessions(user_id: str, app_name: str):
    """List sessions for a user and app"""
    try:
        sessions = await session_service.list_sessions(user_id, app_name)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        await session_service.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Chat API with SSE
```python
# api/chat.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from services.adk_service import adk_service
from services.session_service import session_service
from models.chat import ChatRequest, ChatEvent

router = APIRouter()

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat responses using SSE"""
    try:
        # Validate session
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create event stream
        async def event_stream() -> AsyncGenerator[str, None]:
            try:
                async for event in adk_service.run_agent(
                    agent_name=request.agent_name,
                    session_id=request.session_id,
                    message=request.new_message
                ):
                    yield f"data: {event.model_dump_json()}\n\n"
            except Exception as e:
                yield f"data: {ChatEvent(error=str(e)).model_dump_json()}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Frontend Implementation (Next.js)

### Core Types and Interfaces

```typescript
// types/agent.ts
export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  tools?: string[];
  capabilities?: string[];
}

export interface AgentConfig {
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  topK?: number;
}

// types/session.ts
export interface Session {
  id: string;
  user_id: string;
  app_name: string;
  created_at: Date;
  updated_at: Date;
  state: Record<string, any>;
  events?: SessionEvent[];
}

export interface SessionCreate {
  user_id: string;
  app_name: string;
}

// types/event.ts
export interface SessionEvent {
  id: string;
  author: string;
  content?: EventContent;
  actions?: EventActions;
  timestamp: Date;
}

export interface EventContent {
  parts: EventPart[];
}

export interface EventPart {
  text?: string;
  functionCall?: FunctionCall;
  functionResponse?: FunctionResponse;
  inlineData?: InlineData;
}

export interface FunctionCall {
  name: string;
  args: Record<string, any>;
}

export interface FunctionResponse {
  name: string;
  response: any;
}

export interface InlineData {
  mimeType: string;
  data: string;
}
```

### Service Layer Implementation

```typescript
// services/agentService.ts
import { Agent } from '@/types/agent'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export class AgentService {
  static async listAgents(): Promise<Agent[]> {
    try {
      const response = await fetch(`${API_BASE}/agents/`)
      if (!response.ok) throw new Error('Failed to fetch agents')
      return await response.json()
    } catch (error) {
      console.error('Error listing agents:', error)
      return []
    }
  }

  static async getAgent(id: string): Promise<Agent | null> {
    try {
      const response = await fetch(`${API_BASE}/agents/${id}`)
      if (!response.ok) return null
      return await response.json()
    } catch (error) {
      console.error('Error fetching agent:', error)
      return null
    }
  }
}

// services/sessionService.ts
import { Session, SessionCreate } from '@/types/session'

export class SessionService {
  static async createSession(data: SessionCreate): Promise<Session> {
    try {
      const response = await fetch(`${API_BASE}/sessions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to create session')
      return await response.json()
    } catch (error) {
      console.error('Error creating session:', error)
      throw error
    }
  }

  static async getSession(id: string): Promise<Session | null> {
    try {
      const response = await fetch(`${API_BASE}/sessions/${id}`)
      if (!response.ok) return null
      return await response.json()
    } catch (error) {
      console.error('Error fetching session:', error)
      return null
    }
  }

  static async listSessions(userId: string, appName: string): Promise<Session[]> {
    try {
      const response = await fetch(`${API_BASE}/sessions/?user_id=${userId}&app_name=${appName}`)
      if (!response.ok) return []
      return await response.json()
    } catch (error) {
      console.error('Error listing sessions:', error)
      return []
    }
  }
}

// services/chatService.ts
import { ChatRequest, ChatEvent } from '@/types/event'

export class ChatService {
  static async sendMessage(
    request: ChatRequest,
    onEvent: (event: ChatEvent) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              onEvent(data)
              
              if (data.status === 'complete') {
                onComplete()
                return
              }
            } catch (e) {
              // Ignore invalid JSON
            }
          }
        }
      }
      
      onComplete()
    } catch (error) {
      onError(error as Error)
    }
  }
}
```

### Custom Hooks Implementation

```typescript
// hooks/useAgents.ts
'use client'

import { useState, useEffect } from 'react'
import { Agent } from '@/types/agent'
import { AgentService } from '@/services/agentService'

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadAgents = async () => {
      try {
        setLoading(true)
        const data = await AgentService.listAgents()
        setAgents(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load agents')
      } finally {
        setLoading(false)
      }
    }

    loadAgents()
  }, [])

  return {
    agents,
    loading,
    error,
    refetch: () => {
      setLoading(true)
      setError(null)
      AgentService.listAgents().then(setAgents).catch(setError).finally(() => setLoading(false))
    }
  }
}

// hooks/useSession.ts
'use client'

import { useState, useEffect } from 'react'
import { Session, SessionCreate } from '@/types/session'
import { SessionService } from '@/services/sessionService'

export function useSession(initialData?: SessionCreate) {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createSession = async (data: SessionCreate) => {
    try {
      setLoading(true)
      const newSession = await SessionService.createSession(data)
      setSession(newSession)
      setError(null)
      return newSession
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const refreshSession = async (sessionId: string) => {
    try {
      setLoading(true)
      const refreshedSession = await SessionService.getSession(sessionId)
      setSession(refreshedSession)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh session')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (initialData) {
      createSession(initialData)
    }
  }, [initialData])

  return {
    session,
    loading,
    error,
    createSession,
    refreshSession
  }
}
```

### Advanced Components

#### Message Component with Multiple Content Types
```typescript
// components/chat/Message.tsx
'use client'

import { Message } from '@/types/chat'
import { FunctionCallMessage } from './FunctionCallMessage'
import { CodeExecutionMessage } from './CodeExecutionMessage'
import { ArtifactMessage } from './ArtifactMessage'

interface MessageProps {
  message: Message
  isTyping?: boolean
}

export function Message({ message, isTyping }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`p-3 rounded-lg ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {message.content && (
            <div className="prose prose-sm max-w-none">
              <p>{message.content}</p>
            </div>
          )}
          
          {message.functionCall && (
            <FunctionCallMessage functionCall={message.functionCall} />
          )}
          
          {message.functionResponse && (
            <div className="mt-2 p-2 bg-gray-800 text-green-400 rounded text-sm font-mono">
              <div className="font-semibold">{message.functionResponse.name}:</div>
              <pre className="mt-1 text-xs overflow-x-auto">
                {JSON.stringify(message.functionResponse.response, null, 2)}
              </pre>
            </div>
          )}
          
          {message.codeExecution && (
            <CodeExecutionMessage execution={message.codeExecution} />
          )}
          
          {message.artifact && (
            <ArtifactMessage artifact={message.artifact} />
          )}
          
          {isTyping && (
            <div className="flex items-center gap-1 mt-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          )}
        </div>
        
        <div className={`text-xs mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
```

#### Agent Selection Component
```typescript
// components/agents/AgentSelector.tsx
'use client'

import { Agent } from '@/types/agent'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface AgentSelectorProps {
  agents: Agent[]
  selectedAgent: string | null
  onAgentSelect: (agentId: string) => void
}

export function AgentSelector({ agents, selectedAgent, onAgentSelect }: AgentSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {agents.map((agent) => (
        <Card
          key={agent.id}
          className={`cursor-pointer transition-all hover:shadow-md ${
            selectedAgent === agent.id ? 'ring-2 ring-blue-500' : ''
          }`}
          onClick={() => onAgentSelect(agent.id)}
        >
          <CardHeader>
            <CardTitle className="text-lg">{agent.name}</CardTitle>
            <CardDescription className="text-sm text-gray-600">
              Model: {agent.model}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 mb-3">{agent.description}</p>
            {agent.tools && agent.tools.length > 0 && (
              <div>
                <h4 className="font-medium text-sm mb-2">Available Tools:</h4>
                <div className="flex flex-wrap gap-1">
                  {agent.tools.map((tool) => (
                    <span
                      key={tool}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

## Integration Patterns

### 1. Session Management Pattern

```typescript
// Session management with state synchronization
class SessionManager {
  private sessions = new Map<string, SessionState>()
  
  createSession(userId: string, agentId: string): string {
    const sessionId = generateSessionId()
    this.sessions.set(sessionId, {
      id: sessionId,
      userId,
      agentId,
      messages: [],
      state: {},
      createdAt: new Date()
    })
    return sessionId
  }
  
  async syncWithBackend(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId)
    if (!session) return
    
    try {
      const backendSession = await SessionService.getSession(sessionId)
      if (backendSession) {
        session.state = backendSession.state
        session.lastSync = new Date()
      }
    } catch (error) {
      console.error('Failed to sync session:', error)
    }
  }
}
```

### 2. Event Processing Pattern

```typescript
// Event processing with type safety
class EventProcessor {
  private handlers = new Map<string, EventHandler[]>()
  
  registerHandler(eventType: string, handler: EventHandler): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, [])
    }
    this.handlers.get(eventType)!.push(handler)
  }
  
  processEvent(event: ChatEvent): void {
    const handlers = this.handlers.get(event.type) || []
    handlers.forEach(handler => {
      try {
        handler(event)
      } catch (error) {
        console.error('Event handler error:', error)
      }
    })
  }
}
```

### 3. Error Handling Pattern

```typescript
// Comprehensive error handling
class ErrorHandler {
  static handleApiError(error: any): never {
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.data.message || error.response.statusText}`)
    } else if (error.request) {
      // No response received
      throw new Error('Network error: No response from server')
    } else {
      // Request setup error
      throw new Error(`Request error: ${error.message}`)
    }
  }
  
  static handleWebSocketError(error: Event): void {
    console.error('WebSocket error:', error)
    // Implement reconnection logic
  }
  
  static handleSseError(error: any): void {
    console.error('SSE error:', error)
    // Implement reconnection logic
  }
}
```

## Deployment Considerations

### 1. Containerization

#### Dockerfile for Backend
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile for Frontend
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### 2. Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  redis_data:
```

### 3. Environment Configuration

```bash
# .env.example
# Application
NEXT_PUBLIC_APP_NAME=AI Agent Platform
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Vertex AI
VERTEX_AI_MODEL=gemini-2.5-flash

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
```

### 4. Production Deployment

#### Kubernetes Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT
          valueFrom:
            secretKeyRef:
              name: google-cloud
              key: project-id
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Best Practices and Lessons Learned

### 1. Architecture Best Practices

#### **Separation of Concerns**
- Keep frontend and backend as separate services
- Use well-defined API contracts
- Implement proper error boundaries

#### **State Management**
- Use session-based state for conversations
- Implement optimistic UI updates
- Handle offline/online scenarios gracefully

#### **Performance Optimization**
- Implement streaming for real-time responses
- Use Web Workers for heavy computations
- Optimize bundle sizes with code splitting

### 2. Security Considerations

#### **API Security**
```python
# FastAPI security middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

#### **Authentication & Authorization**
```typescript
// JWT authentication middleware
export function withAuth(handler: NextApiHandler): NextApiHandler {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const token = req.headers.authorization?.replace('Bearer ', '')
    
    if (!token) {
      return res.status(401).json({ error: 'Unauthorized' })
    }
    
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!)
      req.user = decoded
      return handler(req, res)
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' })
    }
  }
}
```

### 3. Monitoring and Observability

#### **Logging Strategy**
```python
# Structured logging with Python
import structlog
import logging

logger = structlog.get_logger()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    logger.info(
        "request_started",
        method=request.method,
        url=str(request.url),
        client_host=request.client.host
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response
```

#### **Error Tracking**
```typescript
// Frontend error tracking with Sentry
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV,
})

export function reportError(error: Error, context?: any) {
  Sentry.captureException(error, {
    extra: context
  })
}
```

### 4. Testing Strategy

#### **Backend Testing**
```python
# pytest fixtures
@pytest.fixture
def mock_agent():
    return Agent(
        name="test_agent",
        model="gemini-2.5-flash",
        instruction="Test instruction"
    )

@pytest.fixture
def test_session():
    return Session(
        id="test_session",
        user_id="test_user",
        app_name="test_app"
    )

# API endpoint tests
@pytest.mark.asyncio
async def test_create_session(client, test_session):
    response = await client.post("/api/v1/sessions/", json={
        "user_id": "test_user",
        "app_name": "test_app"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"
    assert data["app_name"] == "test_app"
```

#### **Frontend Testing**
```typescript
// React component testing with Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChatInterface } from '@/components/chat/ChatInterface'

test('sends message when form is submitted', async () => {
  const mockSendMessage = vi.fn()
  
  render(<ChatInterface onSendMessage={mockSendMessage} />)
  
  const input = screen.getByPlaceholderText('Type your message...')
  const button = screen.getByRole('button', { name: /send/i })
  
  fireEvent.change(input, { target: { value: 'Hello' } })
  fireEvent.click(button)
  
  await waitFor(() => {
    expect(mockSendMessage).toHaveBeenCalledWith('Hello')
  })
})
```

### 5. Performance Optimization

#### **Backend Optimization**
```python
# Connection pooling with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

#### **Frontend Optimization**
```typescript
// React optimization with useMemo and useCallback
const MessageList = React.memo(({ messages }: { messages: Message[] }) => {
  const renderedMessages = useMemo(() => {
    return messages.map(message => ({
      ...message,
      formattedTime: new Date(message.timestamp).toLocaleTimeString()
    }))
  }, [messages])

  return (
    <div>
      {renderedMessages.map(message => (
        <Message key={message.id} message={message} />
      ))}
    </div>
  )
})
```

### 6. Scaling Considerations

#### **Horizontal Scaling**
- Use stateless backend services
- Implement external session storage (Redis)
- Load balance multiple instances
- Use container orchestration (Kubernetes)

#### **Database Scaling**
- Implement read replicas
- Use connection pooling
- Optimize database queries
- Consider database sharding for large datasets

### 7. Cost Optimization

#### **Google Cloud Cost Management**
```python
# Cost-aware model selection
def get_model_for_task(task_complexity: str) -> str:
    models = {
        "simple": "gemini-1.5-flash",
        "complex": "gemini-1.5-pro",
        "expert": "gemini-1.5-ultra"
    }
    return models.get(task_complexity, "gemini-1.5-flash")
```

#### **Resource Optimization**
- Implement auto-scaling based on load
- Use spot instances for non-critical workloads
- Optimize container resource limits
- Monitor and eliminate resource waste

## Conclusion

This implementation guide provides a comprehensive approach to building an AI Agent application using Next.js, FastAPI, and Google ADK. The architecture is designed to be:

1. **Scalable**: Microservices architecture with clear separation of concerns
2. **Maintainable**: Type-safe implementations with comprehensive testing
3. **Production-Ready**: Security, monitoring, and deployment considerations
4. **Extensible**: Plugin-based agent and tool system
5. **User-Friendly**: Real-time streaming with modern UI components

The key to success is following the established patterns from the Google ADK samples while adapting them to work seamlessly with modern web technologies. The combination of Next.js's powerful frontend capabilities and FastAPI's high-performance backend creates an excellent foundation for building sophisticated AI applications.

## Next Steps

1. **Setup Development Environment**: Clone the repository and set up the development environment
2. **Implement Core Features**: Start with basic chat functionality and gradually add advanced features
3. **Add Authentication**: Implement user authentication and authorization
4. **Deploy to Production**: Use the provided Docker configurations for deployment
5. **Monitor and Optimize**: Set up monitoring and continuously optimize performance

This architecture provides a solid foundation for building enterprise-grade AI applications that can scale with your needs.