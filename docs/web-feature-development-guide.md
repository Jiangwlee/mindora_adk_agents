
# Project: adk-web

The [adk-web](https://github.com/google/adk-web/) project is the web-based UI for the Agent Development Kit (ADK).

This document serves as a coding reference for the chat application, providing a detailed analysis of its architecture, key components, and data flow. It is intended to help developers understand the codebase and build similar applications.

# File Index

This table provides an index of the files in the `src/app` directory, along with a description of their purpose and a link to the file on GitHub.

| File | Description | GitHub Link |
| :--- | :--- | :--- |
| `app-routing.module.ts` | Configures the application's routes. | [Link](https://github.com/google/adk-web/blob/main/src/app/app-routing.module.ts) |
| `app.component.html` | The main HTML template for the application. | [Link](https://github.com/google/adk-web/blob/main/src/app/app.component.html) |
| `app.component.scss` | The main stylesheet for the application. | [Link](https://github.com/google/adk-web/blob/main/src/app/app.component.scss) |
| `app.component.spec.ts` | Unit tests for the main application component. | [Link](https://github.com/google/adk-web/blob/main/src/app/app.component.spec.ts) |
| `app.component.ts` | The main component of the application. | [Link](https://github.com/google/adk-web/blob/main/src/app/app.component.ts) |
| `app.module.ts` | The root module of the application. | [Link](https://github.com/google/adk-web/blob/main/src/app/app.module.ts) |
| `components/component.module.ts` | The module that imports and exports all the components. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/component.module.ts) |
| `components/artifact-tab/artifact-tab.component.ts` | A component for displaying and managing artifacts. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/artifact-tab/artifact-tab.component.ts) |
| `components/audio-player/audio-player.component.ts` | A component for playing audio. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/audio-player/audio-player.component.ts) |
| `components/chat/chat.component.ts` | The main component for the chat interface. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/chat/chat.component.ts) |
| `components/edit-json-dialog/edit-json-dialog.component.ts` | A dialog for editing JSON. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/edit-json-dialog/edit-json-dialog.component.ts) |
| `components/eval-tab/eval-tab.component.ts` | A component for evaluating models. | [Link](https/github.com/google/adk-web/blob/main/src/app/components/eval-tab/eval-tab.component.ts) |
| `components/event-tab/event-tab.component.ts` | A component for displaying events. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/event-tab/event-tab.component.ts) |
| `components/json-editor/json-editor.component.ts` | A component for editing JSON. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/json-editor/json-editor.component.ts) |
| `components/pending-event-dialog/pending-event-dialog.component.ts` | A dialog for displaying pending events. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/pending-event-dialog/pending-event-dialog.component.ts) |
| `components/session-tab/session-tab.component.ts` | A component for managing sessions. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/session-tab/session-tab.component.ts) |
| `components/state-tab/state-tab.component.ts` | A component for displaying the application state. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/state-tab/state-tab.component.ts) |
| `components/trace-tab/trace-tab.component.ts` | A component for displaying traces. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/trace-tab/trace-tab.component.ts) |
| `components/view-image-dialog/view-image-dialog.component.ts` | A dialog for viewing images. | [Link](https://github.com/google/adk-web/blob/main/src/app/components/view-image-dialog/view-image-dialog.component.ts) |
| `core/models/AgentRunRequest.ts` | The model for an agent run request. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/AgentRunRequest.ts) |
| `core/models/EvalMetric.ts` | The model for an evaluation metric. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/EvalMetric.ts) |
| `core/models/LiveRequest.ts` | The model for a live request. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/LiveRequest.ts) |
| `core/models/Session.ts` | The model for a session. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/Session.ts) |
| `core/models/Trace.ts` | The model for a trace. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/Trace.ts) |
| `core/models/types.ts` | Common types used in the application. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/models/types.ts) |
| `core/services/agent.service.ts` | A service for interacting with the agent. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/agent.service.ts) |
| `core/services/artifact.service.ts` | A service for managing artifacts. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/artifact.service.ts) |
| `core/services/audio.service.ts` | A service for managing audio. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/audio.service.ts) |
| `core/services/download.service.ts` | A service for downloading files. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/download.service.ts) |
| `core/services/eval.service.ts` | A service for evaluating models. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/eval.service.ts) |
| `core/services/event.service.ts` | A service for managing events. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/event.service.ts) |
| `core/services/feature-flag.service.ts` | A service for managing feature flags. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/feature-flag.service.ts) |
| `core/services/session.service.ts` | A service for managing sessions. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/session.service.ts) |
| `core/services/trace.service.ts` | A service for managing traces. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/trace.service.ts) |
| `core/services/video.service.ts` | A service for managing video. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/video.service.ts) |
| `core/services/websocket.service.ts` | A service for managing WebSockets. | [Link](https://github.com/google/adk-web/blob/main/src/app/core/services/websocket.service.ts) |
| `directives/resizable-bottom.directive.ts` | A directive for making elements resizable from the bottom. | [Link](https://github.com/google/adk-web/blob/main/src/app/directives/resizable-bottom.directive.ts) |
| `directives/resizable-drawer.directive.ts` | A directive for making drawers resizable. | [Link](https://github.com/google/adk-web/blob/main/src/app/directives/resizable-drawer.directive.ts) |


# Chat Application Coding Reference

This document provides a detailed analysis of the chat application's architecture, key components, and data flow. It serves as a reference for developers looking to understand and build similar applications.

## 1. High-Level Overview

The application is a sophisticated chat interface built with Angular. It facilitates interaction with a backend AI agent, supporting text, file uploads, and real-time audio/video streaming. The key technologies employed are:

- **Angular:** For the frontend framework.
- **RxJS:** For managing asynchronous operations and data streams.
- **Server-Sent Events (SSE):** For receiving streaming responses from the agent.
- **WebSockets:** For real-time, bidirectional communication, primarily for audio and video streaming.

## 2. Core Components

### 2.1. [`ChatComponent`](https://github.com/google/adk-web/blob/main/src/app/components/chat/chat.component.ts)

This is the central component of the chat application, orchestrating the entire user interface and interactions.

**Responsibilities:**

- **User Input:** Manages the text input field, file uploads, and audio/video recording controls.
- **Message Display:** Renders the conversation history, including user messages, bot responses, and system events.
- **State Management:** Maintains the application's state, such as the current session, selected agent, and UI visibility.
- **Service Integration:** Coordinates with various services (`AgentService`, `SessionService`, etc.) to handle backend communication and data management.

**Key Logic:**

- **`sendMessage()`:** Triggered when the user sends a message. It constructs an `AgentRunRequest` and calls the `AgentService` to send the request to the backend.
- **Response Handling:** Subscribes to the `AgentService`'s SSE observable to receive streaming responses. It processes these responses to update the chat display with text, thoughts, function calls, and other content.
- **Session Management:** Interacts with the `SessionService` to create, load, and manage user sessions.

### 2.2. [`AgentService`](https://github.com/google/adk-web/blob/main/src/app/core/services/agent.service.ts)

This service is the primary interface for communicating with the backend AI agent.

**Responsibilities:**

- **Sending Requests:** Provides the `runSse()` method to send `AgentRunRequest` objects to the backend.
- **Handling SSE:** Establishes and manages the SSE connection to receive streaming responses from the agent.
- **Loading State:** Maintains a `BehaviorSubject` to track the loading state of the agent, allowing the UI to display loading indicators.

**Key Logic:**

- **`runSse()`:** Uses the browser's `fetch` API to make a POST request to the `/run_sse` endpoint. It then reads the streaming response, decodes it, and emits each event as an observable emission.

### 2.3. [`SessionService`](https://github.com/google/adk-web/blob/main/src/app/core/services/session.service.ts)

This service manages user sessions, which are essential for maintaining conversation history and state.

**Responsibilities:**

- **Session Lifecycle:** Provides methods to `createSession`, `listSessions`, `deleteSession`, and `getSession`.
- **Data Persistence:** While the service itself doesn't handle storage, it provides the API for the application to manage session data with the backend.

### 2.4. [`WebSocketService`](https://github.com/google/adk-web/blob/main/src/app/core/services/websocket.service.ts)

This service handles real-time, bidirectional communication with the backend, primarily for audio and video streaming.

**Responsibilities:**

- **Connection Management:** Establishes, maintains, and closes the WebSocket connection.
- **Message Handling:** Sends and receives messages over the WebSocket. For this application, it's used to stream audio data to the server and receive audio responses.

## 3. Data Flow and Logic

### 3.1. Sending a Message

1.  The user types a message in the `ChatComponent`'s input field and presses Enter.
2.  The `sendMessage()` method in `ChatComponent` is called.
3.  An `AgentRunRequest` object is created, containing the user's message, session ID, and other relevant information.
4.  The `AgentService.runSse()` method is called with the request object.
5.  `AgentService` sends a POST request to the backend's `/run_sse` endpoint.

```typescript
// chat.component.ts
async sendMessage(event: Event) {
  // ...
  const req: AgentRunRequest = {
    appName: this.appName,
    userId: this.userId,
    sessionId: this.sessionId,
    newMessage: {
      'role': 'user',
      'parts': await this.getUserMessageParts(),
    },
    streaming: this.useSse,
    stateDelta: this.updatedSessionState(),
  };
  // ...
  this.agentService.runSse(req).subscribe({
    // ...
  });
  // ...
}
```

### 3.2. Receiving a Response

1.  The backend agent processes the request and sends back a stream of events (SSE).
2.  The `AgentService.runSse()` method receives these events.
3.  Each event is emitted as a new value from the `runSse` observable.
4.  The `ChatComponent` subscribes to this observable and processes each event.
5.  The `processPart()` method in `ChatComponent` is responsible for parsing the event and updating the `messages` array, which is then rendered in the template.

```typescript
// agent.service.ts
runSse(req: AgentRunRequest) {
  // ...
  return new Observable<string>((observer) => {
    fetch(url, {
      // ...
    })
    .then((response) => {
      const reader = response.body?.getReader();
      // ...
      const read = () => {
        reader?.read()
          .then(({done, value}) => {
            // ...
            observer.next(data);
            // ...
          });
      };
      read();
    });
  });
}
```

### 3.3. Session Management

- When the application loads or the user selects a new agent, the `ChatComponent` calls `createSession()` in the `SessionService`.
- The `SessionService` makes a POST request to the backend to create a new session.
- The backend returns a session ID, which is then stored in the `ChatComponent` and used for all subsequent requests.

## 4. Key Data Models

### 4.1. `AgentRunRequest`

This interface defines the structure of a request sent to the agent.

```typescript
export interface AgentRunRequest {
  appName: string;
  userId: string;
  sessionId: string;
  newMessage: any;
  functionCallEventId?: string;
  streaming?: boolean;
  stateDelta?: any;
}
```

### 4.2. `Session`

This interface defines the structure of a session object.

```typescript
export interface Session {
  id?: string;
  appName?: string;
  userId?: string;
  state?: any;
  events?: any;
  messages?: any;
}
```

## 5. Conclusion

This chat application demonstrates a robust architecture for building interactive AI-powered web applications. By understanding the roles of the core components and the data flow between them, developers can effectively build upon and adapt this codebase for their own projects. The use of SSE for streaming responses is particularly noteworthy, as it provides a responsive and real-time user experience.
