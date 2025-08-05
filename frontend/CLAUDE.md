# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Development server**: `npm run serve --backend=http://localhost:8000`
  - This runs `clean-config`, `inject-backend`, and `ng serve` in sequence
  - Backend URL is injected into `src/assets/config/runtime-config.json`
- **Build**: `npm run build`
- **Test**: `npm run test`
- **Watch mode**: `npm run watch`

### Backend Configuration
- **Clean config**: `npm run clean-config`
- **Inject backend**: `npm run inject-backend -- --backend=http://localhost:8000`
- **Required**: Backend URL must be provided when running the serve command

## Architecture Overview

This is an Angular 19 web application for the Agent Development Kit (ADK) that provides a developer UI for agent development and debugging.

### Core Structure
- **Single Page Application**: Uses Angular with Material Design components
- **Modular Architecture**: Organized into components, services, and models
- **Real-time Communication**: WebSocket service for live agent interaction
- **Server-Sent Events**: For streaming agent responses

### Key Services
- **WebSocketService**: Handles real-time audio streaming and message communication (`src/app/core/services/websocket.service.ts`)
- **AgentService**: Manages agent execution via SSE streaming (`src/app/core/services/agent.service.ts`)
- **SessionService**: Handles session management and persistence
- **TraceService**: Manages execution traces and debugging information
- **EventService**: Handles event streaming and processing

### Main Components
- **ChatComponent**: Main chat interface for agent interaction
- **TraceTabComponent**: Displays execution traces and debugging info
- **EventTabComponent**: Shows event streams with trace visualization
- **SessionTabComponent**: Manages agent sessions
- **EvalTabComponent**: Handles agent evaluation and testing
- **StateTabComponent**: Displays agent state information
- **ArtifactTabComponent**: Shows generated artifacts and files

### Data Models
- **Invocation**: Represents agent execution with user content, responses, and intermediate data
- **Content**: Message content with parts and role information
- **LiveRequest**: WebSocket message structure for live agent interaction
- **AgentRunRequest**: Request structure for agent execution

### Backend Integration
- **Configuration**: Backend URL is injected at runtime via `set-backend.js`
- **API Endpoints**: Communicates with ADK API server at configured backend
- **Streaming**: Uses Server-Sent Events for agent response streaming
- **WebSocket**: Real-time audio and message communication

### Development Environment
- **Angular CLI**: Project uses Angular CLI for build and development
- **Material Design**: UI components from Angular Material
- **TypeScript**: Strict TypeScript configuration with Angular compiler options
- **SCSS**: Styling with SCSS preprocessor

### Testing
- **Karma/Jasmine**: Unit testing framework configured
- **Angular Testing**: Angular-specific testing utilities
- **Test Command**: `npm run test` executes all tests

### Build Configuration
- **Production**: Optimized build with budget limits (90MB initial, 800kB component styles)
- **Development**: Source maps and no optimization
- **Output**: Builds to `dist/agent_framework_web` with base href `./`

### Key Dependencies
- **Angular 19**: Core framework
- **Angular Material 19**: UI components
- **RxJS**: Reactive programming
- **ngx-json-viewer**: JSON display component
- **ngx-markdown**: Markdown rendering
- **vanilla-jsoneditor**: JSON editing functionality
- **viz-js**: Graph visualization for traces