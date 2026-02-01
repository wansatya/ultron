# OpenClaw: Complete System Architecture Specification

> Language-agnostic specification for reimplementing OpenClaw in any programming language

**Version**: 2026.1.30
**Repository**: https://github.com/openclaw/openclaw
**License**: MIT

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Purpose & Core Functions](#2-system-purpose--core-functions)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Components](#4-core-components)
5. [Communication Patterns](#5-communication-patterns)
6. [Data Structures & Formats](#6-data-structures--formats)
7. [Protocol Specification](#7-protocol-specification)
8. [External Integrations](#8-external-integrations)
9. [Security & Authentication](#9-security--authentication)
10. [Session Management](#10-session-management)
11. [Message Routing & Queuing](#11-message-routing--queuing)
12. [Tool Execution System](#12-tool-execution-system)
13. [Extension & Plugin Architecture](#13-extension--plugin-architecture)
14. [Deployment Models](#14-deployment-models)
15. [Implementation Guidelines](#15-implementation-guidelines)

---

## 1. Executive Summary

**OpenClaw** is a personal AI assistant gateway that provides:

- **Unified multi-channel messaging**: Connect to 15+ messaging platforms (WhatsApp, Telegram, Discord, Slack, Signal, iMessage, etc.) through a single control plane
- **Persistent AI agent sessions**: Maintain isolated conversation contexts per user/group/channel with automatic session management
- **Tool execution framework**: Execute system commands, browser automation, file operations, and custom tools with sandboxing
- **Local-first architecture**: All data and state remain on the user's device; gateway acts as a personal control plane
- **Cross-platform support**: Works on macOS, Linux, Windows, iOS, and Android with native apps and CLI

**Core Innovation**: OpenClaw separates the messaging gateway (long-running daemon maintaining all provider connections) from the agent runtime (embedded AI with tool execution), enabling reliable multi-channel AI orchestration.

---

## 2. System Purpose & Core Functions

### 2.1 Primary Use Cases

1. **Personal AI Assistant**: Chat with Claude AI through any messaging platform you already use
2. **Multi-Device Control**: Control smart home, servers, and IoT devices through natural language across channels
3. **Workflow Automation**: Schedule tasks, trigger webhooks, and automate cross-platform workflows
4. **Developer Tools**: Execute code, manage git repos, run tests, and debug through conversational interface
5. **Knowledge Hub**: Unified chat history and context across all platforms with searchable transcripts

### 2.2 Design Principles

- **Local-First**: All data stays on user's device; no cloud dependency for core functionality
- **Session Isolation**: Each conversation context is independent; no cross-contamination
- **Stream-First**: Responses stream in real-time with chunking for platform limits
- **Tool-Oriented**: Everything is a tool; extensible through plugins
- **Fail-Safe**: Graceful degradation; continues working even if some channels fail
- **Privacy**: Encrypted credentials; no telemetry; user controls all data

---

## 3. Architecture Overview

### 3.1 Logical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
│  (CLI, macOS App, iOS App, Android App, Web UI, Native Apps)  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ WebSocket (Protocol v3)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Gateway Daemon                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  WebSocket Server (127.0.0.1:18789)                      │  │
│  │  - Client handshake & authentication                     │  │
│  │  - Request/response routing                              │  │
│  │  - Event broadcasting                                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Channel Connectors (Provider Adapters)                  │  │
│  │  - WhatsApp, Telegram, Discord, Slack, Signal, etc.     │  │
│  │  - Message normalization & routing                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Message Router                                           │  │
│  │  - Inbound → Session key mapping                         │  │
│  │  - Binding rules & agent selection                       │  │
│  │  - Deduplication & debouncing                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Queue Manager (Lane-Aware FIFO)                         │  │
│  │  - Per-session serial execution                          │  │
│  │  - Cross-session parallel execution                      │  │
│  │  - Priority lanes & concurrency limits                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Agent Runtime (Embedded Pi)                             │  │
│  │  - Session transcript loading                            │  │
│  │  - LLM invocation with streaming                         │  │
│  │  - Tool execution & result handling                      │  │
│  │  - Response chunking & batching                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Tool Framework                                           │  │
│  │  - Built-in tools (read, write, exec, etc.)             │  │
│  │  - Channel-specific tools                                │  │
│  │  - Custom skills & plugins                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Cron Scheduler                                           │  │
│  │  - Job definition & scheduling                           │  │
│  │  - Webhook handlers                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────┬────────────────────────┬─────────────────┬──────────┘
           │                        │                 │
           ↓                        ↓                 ↓
┌──────────────────┐  ┌────────────────────┐  ┌─────────────────┐
│  Messaging APIs  │  │  LLM Providers     │  │  External Tools │
│  (WhatsApp,      │  │  (Anthropic,       │  │  (Browser,      │
│   Telegram,      │  │   OpenAI,          │  │   Canvas,       │
│   Discord, etc.) │  │   Google, etc.)    │  │   Node Apps)    │
└──────────────────┘  └────────────────────┘  └─────────────────┘
```

### 3.2 Process Model

**Single-Process Architecture**:
- Gateway daemon runs as a single long-lived process
- Agent runtime is **embedded** (not a separate subprocess)
- Channel connectors run in the same process
- Tool execution may spawn subprocesses for isolation

**Multi-Client Support**:
- Multiple clients can connect to the same gateway simultaneously
- Each client gets its own WebSocket connection
- Events broadcast to all connected clients
- Request/response routing via unique request IDs

---

## 4. Core Components

### 4.1 Gateway Daemon

**Responsibility**: Single source of truth for all messaging connections, session state, and orchestration

**Lifecycle**:
1. Load configuration from `~/.openclaw/openclaw.json`
2. Initialize channel providers (authenticate, restore sessions)
3. Start WebSocket server on configured bind address & port
4. Begin heartbeat & presence tracking
5. Accept client connections and route requests
6. Gracefully shutdown on signal (SIGTERM/SIGINT)

**Key Modules**:
- `WebSocketServer`: Accept connections, authenticate, route frames
- `ChannelManager`: Lifecycle for all channel providers
- `MessageRouter`: Inbound message → session key resolution
- `QueueManager`: Lane-aware FIFO queue with concurrency control
- `AgentRunner`: Embedded Pi agent execution
- `CronScheduler`: Job scheduling & webhook handling
- `ConfigManager`: Hot-reload configuration changes
- `PresenceTracker`: Monitor connected devices & heartbeats

**Configuration**:
```json5
{
  gateway: {
    bind: "loopback" | "tailnet" | "0.0.0.0",
    port: 18789,
    mode: "local" | "remote",
    auth: {
      token: "optional_shared_secret",
      password: "optional_password"
    },
    tls: {
      enabled: false,
      cert: "/path/to/cert.pem",
      key: "/path/to/key.pem"
    }
  }
}
```

**State Management**:
- Gateway is **stateless** except for:
  - Active channel provider sessions (in-memory)
  - Queue state (in-flight runs)
  - Connected client list (WebSocket connections)
- All persistent state lives in filesystem (sessions, config)

---

### 4.2 Agent Runtime

**Responsibility**: Execute AI agent turns with tool calling and response streaming

**Implementation**: Embedded Pi-mono instance (not RPC subprocess)

**Execution Flow**:
```
1. Receive message from queue
2. Load session transcript (JSONL)
3. Build system prompt from workspace files
4. Create agent session with tool list
5. Stream LLM response with tool invocations
6. Execute tools synchronously
7. Continue agent loop until completion
8. Persist updated transcript
9. Return final response summary
```

**Key Functions**:
- `runEmbeddedPiAgent()`: Main entry point
- `createAgentSession()`: Initialize Pi agent with context
- `buildSystemPrompt()`: Assemble bootstrap files + tools
- `executeToolCall()`: Route tool invocation to handler
- `streamBlockReply()`: Chunk & send response blocks
- `persistTranscript()`: Write session JSONL

**Configuration**:
```json5
{
  agents: {
    defaults: {
      model: "anthropic/claude-opus-4-5-20251101",
      maxConcurrent: 4,
      blockStreamingDefault: "off",
      sandbox: {
        enabled: false,
        workspaceRoot: "/tmp/sandbox"
      }
    },
    list: [
      {
        id: "main",
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        model: "anthropic/claude-sonnet-4-5-20250929"
      }
    ]
  }
}
```

**Response Streaming**:
- Agent produces blocks in real-time (text, tool use, tool results)
- `onBlockReply` callback emits chunks as they arrive
- Chunking respects platform limits (4096 chars for WhatsApp, 2000 for Telegram)
- Paragraph-aware splitting to avoid mid-sentence cuts
- Batching small chunks to reduce API calls

---

### 4.3 Session Manager

**Responsibility**: Persistent conversation context isolation and recovery

**Storage Format**: JSONL (JSON Lines)
- Each line is one message turn (user, assistant, tool result)
- Human-readable and streamable
- Append-only for reliability

**Session Key Derivation**:
```
Format: agent:<agentId>:<scopeKey>

Examples:
- DM (default): agent:main:main
- DM (per-peer): agent:main:whatsapp:+15551234567
- Group chat: agent:main:discord:group:123456789
- Thread: agent:main:slack:thread:T123:C456:1234567890.123456
- Cron job: cron:daily-backup
- Webhook: hook:uuid-1234-5678-abcd
```

**Scope Modes** (configurable):
- `main`: All DMs across all channels collapse into one session
- `per-peer`: Separate session per sender (cross-channel)
- `per-channel-peer`: Separate session per channel + sender
- `per-account-channel-peer`: Separate session per account + channel + sender

**Session Reset**:
- **Daily reset**: Default at 4 AM local time (configurable)
- **Idle timeout**: Optional timeout after N minutes of inactivity
- **Manual reset**: User can reset via command or API

**Session Index** (`sessions.json`):
```json5
{
  "agent:main:main": {
    "sessionId": "sess_abc123",
    "updatedAt": 1737264000000,
    "channel": "whatsapp",
    "chatType": "dm",
    "from": "+15551234567",
    "totalTokens": 2000,
    "origin": {
      "label": "Alice",
      "provider": "whatsapp"
    }
  }
}
```

**Transcript Pruning**:
- Before each LLM call, prune old tool results to fit context window
- Keep recent messages and tool results
- Summarize truncated history if needed

**File Locations**:
```
~/.openclaw/agents/<agentId>/sessions/
  ├── sessions.json (index)
  └── <sessionId>.jsonl (transcript)
```

---

### 4.4 Channel Connectors

**Responsibility**: Adapt platform-specific APIs to unified message envelope

**Interface**:
```typescript
interface ChannelProvider {
  // Lifecycle
  initialize(): Promise<void>
  shutdown(): Promise<void>

  // Identity
  getStatus(): ChannelStatus
  getAccounts(): Account[]

  // Inbound
  onInboundMessage(handler: (msg: InboundMessage) => void): void

  // Outbound
  sendMessage(params: SendParams): Promise<SendResult>

  // Optional features
  markAsRead?(chatId: string, messageId: string): Promise<void>
  setTyping?(chatId: string, enabled: boolean): Promise<void>
  addReaction?(chatId: string, messageId: string, emoji: string): Promise<void>
  uploadMedia?(file: Buffer, type: string): Promise<MediaUrl>
}
```

**Built-In Channels**:

| Channel | Protocol | Library | Auth Method | Features |
|---------|----------|---------|-------------|----------|
| WhatsApp | Baileys (WS) | `@whiskeysockets/baileys` | QR code pairing | Groups, media, reactions, status |
| Telegram | Bot API (HTTP) | `grammy` | Bot token | Groups, topics, reactions, inline keyboard |
| Discord | Gateway WS + HTTP | `discord.js` | Bot token | Guilds, threads, reactions, embeds, slash commands |
| Slack | Events API | `@slack/bolt` | OAuth token | Channels, threads, reactions, blocks, slash commands |
| Signal | signal-cli RPC | `signal-cli` binary | Phone # + PIN | Groups, media |
| iMessage | imsg RPC | `imsg` binary | System auth | Media, effects |
| Google Chat | Webhook (HTTP) | Google Chat API | Service account | Threads, cards |
| WebChat | WebSocket | Built-in | Anonymous | Static UI, file upload |

**Extension Channels** (plugins):
- BlueBubbles, Matrix, Microsoft Teams, Zalo, Zalo Personal, Mattermost, LINE, GroupMe, Facebook Messenger, etc.

**Message Normalization**:
- Convert platform-specific message format to `InboundMessage` envelope
- Extract media URLs and metadata
- Parse threading info (reply-to, thread ID)
- Resolve display names and sender IDs

**Outbound Delivery**:
- Apply platform-specific limits (char count, media types)
- Format with replies/threading if supported
- Retry with exponential backoff (3 attempts)
- Handle rate limits and backpressure

---

### 4.5 Message Router

**Responsibility**: Map inbound messages to agent workspaces (sessions)

**Routing Rules** (priority order):
1. **Exact peer match**: channel + peer ID
2. **Guild/team match**: Discord guild or Slack workspace
3. **Account match**: Multi-account per channel
4. **Channel match**: Any account on that channel
5. **Default agent**: First in list or explicitly marked as default

**Binding Configuration**:
```json5
{
  agents: {
    list: [
      {
        id: "main",
        bindings: {
          channels: ["whatsapp", "telegram"],
          peers: {
            whatsapp: ["+15551234567"],
            telegram: ["@alice"]
          },
          guilds: {
            discord: ["123456789"]
          }
        }
      },
      {
        id: "work",
        bindings: {
          channels: ["slack"],
          teams: {
            slack: ["T01234567"]
          }
        }
      }
    ]
  }
}
```

**Broadcast Groups**:
- Run multiple agents for the same inbound message
- Useful for testing or multi-persona bots
- Each agent gets its own session key

**Deduplication**:
- Track recent message IDs (5-minute window)
- Skip duplicate messages from platform retries

**Debouncing**:
- Batch rapid messages into single agent run (default 2s)
- Per-channel configurable debounce window
- Useful for copy-paste multi-line messages

---

### 4.6 Queue Manager

**Responsibility**: Serialize agent runs per session while allowing parallelism across sessions

**Lane-Aware FIFO Queue**:
- Each session gets its own lane: `session:<sessionKey>`
- Global lanes: `main`, `cron`, `subagent`
- Lane capacity = 1 for session lanes (serial execution)
- Lane capacity = N for global lanes (parallel execution)

**Queue Modes** (per inbound message):
- `steer`: Inject into current run (skip pending tool calls)
- `followup`: Queue for next turn
- `collect`: Batch messages into one followup (default)
- `interrupt`: Abort current run, execute new message

**Configuration**:
```json5
{
  messages: {
    queue: {
      mode: "collect",
      debounceMs: 1000,
      cap: 20,
      drop: "old" | "new" | "summarize"
    }
  }
}
```

**Overflow Policies**:
- `old`: Drop oldest queued message
- `new`: Drop newest incoming message
- `summarize`: Summarize queued messages into one

**Priority**:
- System messages (pairing, commands) bypass queue
- User messages queue normally
- Cron jobs use dedicated lane

---

### 4.7 Tool Framework

**Responsibility**: Execute actions during agent turns

**Tool Interface**:
```typescript
interface Tool {
  name: string
  description: string
  schema: JSONSchema
  invoke(input: unknown, context: ToolContext): Promise<ToolResult>
}

interface ToolContext {
  agentId: string
  sessionKey: string
  workspace: string
  channel?: string
  user?: UserInfo
}

interface ToolResult {
  success: boolean
  output?: string
  error?: string
  metadata?: Record<string, unknown>
}
```

**Built-In Tools**:
- **File operations**: `read`, `write`, `edit`, `glob`, `grep`
- **System**: `exec`, `bash`
- **Browser**: `browser.snapshot`, `browser.action`, `browser.upload`
- **Canvas**: `canvas.create`, `canvas.update`, `canvas.render`
- **Session**: `sessions.list`, `sessions.get`, `sessions.patch`, `sessions.reset`
- **Gateway**: `node.invoke`, `channels.status`, `config.get`, `config.set`
- **Cron**: `cron.list`, `cron.create`, `cron.delete`

**Channel-Specific Tools**:
- **WhatsApp**: `whatsapp.send`, `whatsapp.groups`, `whatsapp.status`
- **Telegram**: `telegram.send`, `telegram.pin`, `telegram.restrict`
- **Discord**: `discord.send`, `discord.embed`, `discord.role`
- **Slack**: `slack.send`, `slack.upload`, `slack.pin`

**Tool Policy**:
```json5
{
  tools: {
    policy: {
      deny: ["exec", "bash"],  // Block these tools
      allow: ["*"]             // Allow all others
    }
  }
}
```

**Sandboxing**:
- Optional per-workspace sandbox
- Chroot to workspace directory
- Restrict file access outside workspace
- Network isolation (optional)

---

### 4.8 Cron Scheduler

**Responsibility**: Execute scheduled tasks and webhooks

**Job Definition**:
```json5
{
  cron: {
    timezone: "America/Los_Angeles",
    jobs: [
      {
        id: "daily-backup",
        schedule: "0 2 * * *",  // 2 AM daily
        agent: "main",
        message: "Run backup script",
        enabled: true
      }
    ]
  }
}
```

**Webhook Handlers**:
- HTTP POST to `/webhook/:hookId`
- Trigger agent run with webhook payload
- Return JSON response

**Session Key**: `cron:<jobId>` or `hook:<hookId>`

**Scheduling Library**: `node-cron` or equivalent

---

## 5. Communication Patterns

### 5.1 Inbound Message Flow

```
1. Channel event (WhatsApp message, Discord mention, etc.)
   ↓
2. Channel connector normalizes to InboundMessage envelope
   ↓
3. Message router applies deduplication cache
   ↓
4. Router resolves session key via binding rules
   ↓
5. Debouncer batches rapid messages (if configured)
   ↓
6. Queue manager enqueues into session lane
   ↓
7. Lane becomes available, dequeue message
   ↓
8. Agent runtime loads session transcript
   ↓
9. LLM generates response with tool calls
   ↓
10. Tools execute synchronously
   ↓
11. Response blocks stream via callback
   ↓
12. Chunker splits text for platform limits
   ↓
13. Channel connector sends outbound message
   ↓
14. User sees reply in their messaging app
   ↓
15. Session transcript persisted with full turn
```

### 5.2 Outbound Send Flow

```
1. Client or agent calls `chat.send` method
   ↓
2. Gateway resolves target channel + peer ID
   ↓
3. Apply message chunking (respect char limit)
   ↓
4. Format with threading info if supported
   ↓
5. Channel connector attempts send with retry loop
   ↓
6. Exponential backoff on transient failures (3 attempts)
   ↓
7. Permanent failures reported to client
   ↓
8. Success: delivery ACK with message ID
```

### 5.3 Client-Gateway Handshake

```
1. Client opens WebSocket to gateway
   ↓
2. Client sends `connect` request (MANDATORY first frame)
   ↓
3. Gateway validates protocol version
   ↓
4. Gateway authenticates device (token or pairing)
   ↓
5. Gateway responds with `hello-ok` payload
   ↓
6. Client subscribes to events (optional)
   ↓
7. Client begins sending requests
   ↓
8. Gateway broadcasts events to all clients
   ↓
9. Gateway emits `tick` event every ~15s
   ↓
10. Client responds with presence snapshot
   ↓
11. Gateway tracks last tick per device
   ↓
12. Stale clients (no tick >45s) are disconnected
```

### 5.4 Agent Execution Loop

```
1. Queue dequeues message for session lane
   ↓
2. runEmbeddedPiAgent() invoked
   ↓
3. Load session transcript from JSONL
   ↓
4. Build system prompt from workspace files
   ↓
5. Create Pi agent session with tools
   ↓
6. LLM streams response blocks:
   a. Text block → onBlockReply callback
   b. Tool use block → execute tool, get result
   c. Loop until completion
   ↓
7. Final transcript written to JSONL
   ↓
8. Session index updated with token counts
   ↓
9. Gateway emits `agent.complete` event
   ↓
10. Queue releases lane for next message
```

---

## 6. Data Structures & Formats

### 6.1 Session Transcript (JSONL)

**Format**: One JSON object per line, no trailing comma

**User Turn**:
```json
{
  "role": "user",
  "type": "text",
  "body": "Hello world",
  "timestamp": 1737264000000,
  "origin": {
    "channel": "whatsapp",
    "from": "+15551234567",
    "label": "Alice"
  }
}
```

**Assistant Turn with Tool Use**:
```json
{
  "role": "assistant",
  "type": "text",
  "body": "I'll help you check that file.",
  "timestamp": 1737264001000,
  "toolUse": [
    {
      "id": "tool_abc123",
      "name": "read",
      "input": {
        "file_path": "/home/user/file.txt"
      }
    }
  ]
}
```

**Tool Result**:
```json
{
  "role": "user",
  "type": "toolResult",
  "timestamp": 1737264002000,
  "toolResultList": [
    {
      "toolUseId": "tool_abc123",
      "content": "file contents here...",
      "isError": false
    }
  ]
}
```

**Extended Thinking** (if applicable):
```json
{
  "role": "assistant",
  "type": "text",
  "body": "Based on the analysis...",
  "timestamp": 1737264003000,
  "thinking": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step..."
    }
  ]
}
```

### 6.2 Session Index (JSON)

**File**: `~/.openclaw/agents/<agentId>/sessions/sessions.json`

```json5
{
  "agent:main:main": {
    "sessionId": "sess_abc123",
    "updatedAt": 1737264000000,
    "channel": "whatsapp",
    "provider": "whatsapp",
    "chatType": "dm",
    "from": "+15551234567",
    "fromName": "Alice",
    "inputTokens": 1200,
    "outputTokens": 800,
    "totalTokens": 2000,
    "contextTokens": 500,
    "origin": {
      "label": "Alice",
      "provider": "whatsapp",
      "from": "+15551234567",
      "chatType": "dm"
    },
    "lastMessage": "What's the weather like?",
    "lastReply": "The weather is sunny and 75°F."
  },
  "agent:main:discord:group:123456789": {
    "sessionId": "sess_xyz789",
    "updatedAt": 1737264000000,
    "channel": "discord",
    "chatType": "group",
    "displayName": "#general",
    "totalTokens": 5000,
    "origin": {
      "label": "#general",
      "provider": "discord",
      "chatType": "group",
      "groupId": "123456789"
    }
  }
}
```

### 6.3 InboundMessage Envelope

**Purpose**: Unified internal representation of messages from any channel

```typescript
interface InboundMessage {
  // Identity
  provider: string                    // "whatsapp", "telegram", "discord", etc.
  accountId?: string                  // For multi-account support
  peerId: string                      // User/group ID from provider
  peerName?: string                   // Display name
  senderId: string                    // Who sent this message
  senderName?: string                 // Sender display name

  // Content
  body: string                        // Message text (may be empty if media-only)
  commandBody?: string                // Raw text for directive parsing
  chatType: "dm" | "group" | "channel" | "thread"

  // Threading
  replyToId?: string                  // Message ID being replied to
  replyToBody?: string                // Quoted text
  replyToSender?: string              // Original sender
  threadId?: string                   // Thread/topic ID

  // Media
  mediaUrls?: string[]                // Array of media URLs
  mediaTypes?: string[]               // "image", "audio", "video", "document"
  mediaCaptions?: string[]            // Captions for each media

  // Metadata
  messageId: string                   // Provider message ID
  timestamp: number                   // Unix timestamp (ms)
  isEdited?: boolean                  // Message was edited
  isDelete?: boolean                  // Message was deleted
  mentions?: string[]                 // User IDs mentioned
  reactions?: Reaction[]              // Reactions to this message
}

interface Reaction {
  emoji: string
  userId: string
  userName?: string
}
```

### 6.4 Configuration Schema

**File**: `~/.openclaw/openclaw.json` (JSON5 format, comments allowed)

```json5
{
  // Agent definitions
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: "anthropic/claude-opus-4-5-20251101",
      models: {
        // Fallback models
        "fast": "anthropic/claude-sonnet-4-5-20250929",
        "thinking": "anthropic/claude-sonnet-4-5-20250929"
      },
      blockStreamingDefault: "off",  // "off", "text_end", "text_start"
      blockStreamingBreak: "text_end",
      maxConcurrent: 4,
      sandbox: {
        enabled: false,
        workspaceRoot: "/tmp/sandbox"
      }
    },
    list: [
      {
        id: "main",
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        model: "anthropic/claude-sonnet-4-5-20250929",
        bindings: {
          channels: ["whatsapp", "telegram"],
          peers: {
            whatsapp: ["+15551234567"]
          }
        }
      }
    ]
  },

  // Channel configurations
  channels: {
    whatsapp: {
      allowFrom: ["+1234567890"],  // Allowlist for DMs
      groups: {
        "*": {
          requireMention: true,  // Require @mention to respond
          keywords: ["!bot"]     // Or trigger keywords
        },
        "120363XXXXX@g.us": {
          requireMention: false  // Auto-respond in this group
        }
      },
      blockStreaming: false,
      historyLimit: 5  // Include last 5 messages as context
    },
    telegram: {
      allowFrom: ["@alice", "123456789"],
      groups: {
        "*": { requireMention: true }
      }
    },
    discord: {
      allowGuilds: ["123456789"],
      channels: {
        "*": { requireMention: true },
        "987654321": { requireMention: false }
      }
    },
    slack: {
      allowWorkspaces: ["T01234567"],
      channels: {
        "*": { requireMention: true }
      }
    }
  },

  // Session behavior
  session: {
    dmScope: "main",  // "main", "per-peer", "per-channel-peer", "per-account-channel-peer"
    reset: {
      mode: "daily",  // "daily", "idle", "manual"
      atHour: 4,      // Daily reset at 4 AM
      idleMinutes: 120  // Reset after 2 hours idle
    },
    identityLinks: {
      // Link identities across channels (same session)
      "user1": ["whatsapp:+15551234567", "telegram:@alice", "discord:123456789"]
    }
  },

  // Message handling
  messages: {
    inbound: {
      debounceMs: 2000,  // Batch rapid messages
      byChannel: {
        whatsapp: { debounceMs: 3000 },
        telegram: { debounceMs: 1000 }
      }
    },
    queue: {
      mode: "collect",  // "collect", "steer", "followup", "interrupt"
      debounceMs: 1000,
      cap: 20,          // Max queued messages
      drop: "old"       // "old", "new", "summarize"
    },
    groupChat: {
      historyLimit: 5,   // Include last N messages
      mentionPatterns: ["@bot", "!bot"]
    }
  },

  // Gateway settings
  gateway: {
    bind: "loopback",  // "loopback", "tailnet", "0.0.0.0"
    port: 18789,
    mode: "local",     // "local", "remote"
    auth: {
      token: "optional_shared_secret",
      password: "optional_password"
    },
    tls: {
      enabled: false,
      cert: "/path/to/cert.pem",
      key: "/path/to/key.pem"
    }
  },

  // Tool execution
  tools: {
    policy: {
      deny: [],    // Block these tools
      allow: ["*"] // Allow all others
    },
    exec: {
      applyPatch: true,  // Apply exec-guard patch
      sandbox: {
        enabled: false
      }
    }
  },

  // Cron jobs
  cron: {
    timezone: "America/Los_Angeles",
    jobs: [
      {
        id: "daily-backup",
        schedule: "0 2 * * *",
        agent: "main",
        message: "Run backup",
        enabled: true
      }
    ]
  },

  // Logging
  logging: {
    level: "info",  // "silent", "error", "warn", "info", "debug", "trace"
    file: "~/.openclaw/logs/gateway.log"
  }
}
```

---

## 7. Protocol Specification

### 7.1 WebSocket Protocol v3

**Transport**: WebSocket with text frames (JSON payloads)

**Frame Types**:
1. **Request**: Client → Server
2. **Response**: Server → Client
3. **Event**: Server → Client (broadcast)

**MANDATORY First Frame**: Client MUST send `connect` request before any other communication

### 7.2 Request/Response

**Request Frame**:
```json
{
  "type": "req",
  "id": "unique_request_id",
  "method": "method_name",
  "params": {
    // Method-specific parameters
  }
}
```

**Response Frame**:
```json
{
  "type": "res",
  "id": "unique_request_id",
  "ok": true,
  "payload": {
    // Method-specific response
  }
}
```

**Error Response**:
```json
{
  "type": "res",
  "id": "unique_request_id",
  "ok": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error",
    "details": {}
  }
}
```

### 7.3 Handshake (Connect Request)

**Client → Server**:
```json
{
  "type": "req",
  "id": "1",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "2026.1.30",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "auth": {
      "token": "shared_secret_if_configured"
    },
    "device": {
      "id": "device_fingerprint",
      "publicKey": "base64_public_key",
      "signature": "base64_signature",
      "signedAt": 1737264000000,
      "nonce": "random_nonce"
    }
  }
}
```

**Server → Client (Success)**:
```json
{
  "type": "res",
  "id": "1",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "policy": {
      "tickIntervalMs": 15000
    },
    "auth": {
      "deviceToken": "issued_token",
      "role": "operator",
      "scopes": ["operator.read", "operator.write"]
    }
  }
}
```

### 7.4 Core Methods

#### **agent** (Run Agent)
```json
// Request
{
  "method": "agent",
  "params": {
    "sessionKey": "agent:main:main",
    "message": "What's the weather?",
    "agent": "main",
    "mode": "stream"
  }
}

// Response (streaming events via separate event frames)
{
  "ok": true,
  "payload": {
    "runId": "run_abc123",
    "sessionKey": "agent:main:main"
  }
}
```

#### **chat.send** (Send Message)
```json
// Request
{
  "method": "chat.send",
  "params": {
    "channel": "whatsapp",
    "accountId": "optional_account",
    "to": "+15551234567",
    "body": "Hello from OpenClaw!",
    "mediaUrls": ["https://example.com/image.jpg"],
    "replyToId": "message_id"
  }
}

// Response
{
  "ok": true,
  "payload": {
    "messageId": "sent_message_id",
    "timestamp": 1737264000000
  }
}
```

#### **chat.history** (Fetch Transcript)
```json
// Request
{
  "method": "chat.history",
  "params": {
    "sessionKey": "agent:main:main",
    "limit": 50,
    "before": "message_id"
  }
}

// Response
{
  "ok": true,
  "payload": {
    "messages": [
      // Array of transcript turns
    ],
    "hasMore": true
  }
}
```

#### **sessions.list** (List Sessions)
```json
// Request
{
  "method": "sessions.list",
  "params": {
    "agent": "main"
  }
}

// Response
{
  "ok": true,
  "payload": {
    "sessions": [
      {
        "sessionKey": "agent:main:main",
        "sessionId": "sess_abc123",
        "updatedAt": 1737264000000,
        "origin": {
          "label": "Alice",
          "provider": "whatsapp"
        }
      }
    ]
  }
}
```

#### **config.get** (Get Configuration)
```json
// Request
{
  "method": "config.get",
  "params": {
    "path": "agents.defaults.model"
  }
}

// Response
{
  "ok": true,
  "payload": {
    "value": "anthropic/claude-opus-4-5-20251101"
  }
}
```

#### **channels.status** (Channel Status)
```json
// Request
{
  "method": "channels.status",
  "params": {
    "probe": false  // Set true to probe connectivity
  }
}

// Response
{
  "ok": true,
  "payload": {
    "channels": [
      {
        "provider": "whatsapp",
        "status": "connected",
        "accounts": [
          {
            "accountId": "default",
            "identity": "+15551234567",
            "displayName": "My Number"
          }
        ]
      }
    ]
  }
}
```

### 7.5 Event Broadcasting

**Event Frame**:
```json
{
  "type": "event",
  "event": "event_name",
  "payload": {
    // Event-specific data
  },
  "seq": 123,  // Sequence number (optional)
  "stateVersion": 456  // State version (optional)
}
```

**Event Types**:

#### **agent.block** (Agent Response Block)
```json
{
  "event": "agent.block",
  "payload": {
    "runId": "run_abc123",
    "sessionKey": "agent:main:main",
    "block": {
      "type": "text",
      "text": "Here's the answer..."
    }
  }
}
```

#### **agent.complete** (Agent Run Complete)
```json
{
  "event": "agent.complete",
  "payload": {
    "runId": "run_abc123",
    "sessionKey": "agent:main:main",
    "summary": {
      "inputTokens": 1200,
      "outputTokens": 800,
      "totalTokens": 2000
    }
  }
}
```

#### **chat.inbound** (Incoming Message)
```json
{
  "event": "chat.inbound",
  "payload": {
    "provider": "whatsapp",
    "from": "+15551234567",
    "body": "Hello!",
    "chatType": "dm",
    "messageId": "msg_123"
  }
}
```

#### **tick** (Heartbeat)
```json
{
  "event": "tick",
  "payload": {
    "timestamp": 1737264000000
  }
}
```

**Client Response to Tick** (via presence update or keep-alive message)

### 7.6 Authentication Modes

**1. Local Auto-Approve** (loopback/tailnet):
- No authentication required
- Client connects immediately

**2. Token Authentication**:
- Gateway configured with shared token
- Client sends token in `auth.token` field

**3. Device Pairing**:
- Client generates public/private key pair
- Client signs challenge with private key
- Gateway verifies signature and issues device token
- Future connections use device token

**4. Password Authentication**:
- Gateway configured with password
- Client sends password in `auth.password` field

---

## 8. External Integrations

### 8.1 Messaging Platform APIs

| Platform | API Type | Authentication | Rate Limits | Webhook Support |
|----------|----------|----------------|-------------|-----------------|
| WhatsApp (Baileys) | WebSocket | QR pairing | None (personal account) | N/A (WS push) |
| Telegram Bot API | HTTPS (REST) | Bot token | 30 msg/sec | Yes (polling or webhook) |
| Discord | WebSocket + REST | Bot token | 50 req/sec, 5 msg/5sec per channel | N/A (WS push) |
| Slack | HTTPS (REST) + Events API | OAuth token | Tier-based (1+ req/min) | Yes (Events API) |
| Signal (signal-cli) | Local RPC | Phone # + PIN | None | N/A (polling) |
| iMessage (imsg) | Local RPC | System keychain | None | N/A (polling) |
| Google Chat | HTTPS (REST) | Service account | 60 req/min | Yes |
| Matrix | HTTPS (REST) | Access token | Server-dependent | Yes (sync API) |

### 8.2 LLM Provider APIs

| Provider | API Endpoint | Auth | Features | Rate Limits |
|----------|--------------|------|----------|-------------|
| Anthropic | `https://api.anthropic.com` | API key | Extended thinking, vision, tool use | Tier-based (requests + tokens) |
| OpenAI | `https://api.openai.com` | API key | Function calling, vision, embeddings | Tier-based (tokens/min) |
| Google Gemini | `https://generativelanguage.googleapis.com` | API key | Vision, grounding, extended thinking | 60 req/min (free tier) |
| OpenRouter | `https://openrouter.ai` | API key | Multi-model routing | Model-dependent |
| GitHub Copilot | `https://api.githubcopilot.com` | Device token | Code completion, chat | Usage-based |

**Request Format** (Anthropic Messages API):
```json
POST /v1/messages
{
  "model": "claude-opus-4-5-20251101",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "Hello, Claude!"
    }
  ],
  "tools": [
    {
      "name": "read",
      "description": "Read a file",
      "input_schema": {
        "type": "object",
        "properties": {
          "file_path": { "type": "string" }
        },
        "required": ["file_path"]
      }
    }
  ],
  "stream": true
}
```

**Response Format** (Streaming):
```
event: message_start
data: {"type":"message_start","message":{"id":"msg_123",...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hello"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_stop
data: {"type":"message_stop"}
```

### 8.3 Browser Automation (Chrome DevTools Protocol)

**Connection**: WebSocket to Chrome instance

**Launch Command**:
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile
```

**CDP Commands**:
- `Page.navigate`: Load URL
- `Page.captureScreenshot`: Take screenshot
- `Runtime.evaluate`: Execute JavaScript
- `Input.dispatchMouseEvent`: Click
- `Input.dispatchKeyEvent`: Type text
- `DOM.querySelector`: Find element

**Tool Interface**:
```json
{
  "name": "browser.action",
  "input": {
    "action": "click",
    "selector": "button.submit",
    "url": "https://example.com"
  }
}
```

### 8.4 Canvas (Live UI Hosting)

**Architecture**:
- HTTP file server on port 18793
- WebSocket for live updates
- A2UI framework (HTML + JS)

**Workflow**:
1. Agent creates canvas with `canvas.create`
2. Gateway generates HTML page
3. Client opens URL in browser/webview
4. Agent updates canvas via `canvas.update`
5. Real-time updates via WebSocket

**A2UI Format**:
```html
<!DOCTYPE html>
<html>
<head>
  <script src="/a2ui.js"></script>
</head>
<body>
  <div id="app"></div>
  <script>
    a2ui.render({
      type: 'container',
      children: [
        { type: 'text', value: 'Hello from Canvas' },
        { type: 'button', label: 'Click Me', action: 'handle_click' }
      ]
    });
  </script>
</body>
</html>
```

### 8.5 Node Apps (iOS/Android/macOS)

**Connection**: WebSocket to gateway with `role: node`

**Capabilities**:
- Camera capture
- Screen recording
- Canvas rendering (native webview)
- Location access
- Voice input/output
- Push notifications

**Node Commands** (invoked via `node.invoke`):
```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "device_123",
    "command": "camera.capture",
    "args": {
      "camera": "front"
    }
  }
}
```

**Response**:
```json
{
  "ok": true,
  "payload": {
    "imageUrl": "https://gateway/media/abc123.jpg"
  }
}
```

---

## 9. Security & Authentication

### 9.1 Threat Model

**Assumptions**:
- User's device is trusted
- Gateway runs on user's local network or trusted VPN
- Messaging provider APIs are trusted
- LLM provider APIs are trusted

**Threats**:
- Unauthorized access to gateway (remote connections)
- Message injection from untrusted senders
- Tool execution with malicious payloads
- Credential theft from filesystem
- Man-in-the-middle attacks (remote connections)

### 9.2 Authentication Mechanisms

**1. Loopback Auto-Approve**:
- Clients connecting from `127.0.0.1` or `::1` auto-approve
- No authentication required
- Fast UX for local clients

**2. Tailnet Auto-Approve**:
- Clients connecting from Tailscale IP range auto-approve
- Assumes Tailscale handles authentication
- Fast UX for trusted devices

**3. Device Pairing**:
- New device generates Ed25519 key pair
- Device signs challenge with private key
- Gateway verifies signature
- Gateway issues long-lived device token
- Token stored on device for future connections

**Pairing Flow**:
```
1. Client connects with no auth
2. Gateway responds with `hello-pair-required`
3. Gateway generates pairing code (6 digits)
4. User approves pairing code on gateway UI
5. Client sends signed challenge
6. Gateway verifies signature
7. Gateway issues device token
8. Client stores token for future use
```

**4. Token Authentication**:
- Gateway configured with shared secret
- All clients must send token in `auth.token` field
- Token validation on every connection

**5. Password Authentication**:
- Gateway configured with password
- Clients must send password in `auth.password` field
- Password hashed with bcrypt

### 9.3 Message Authorization

**DM Pairing** (default):
- New sender requires pairing code approval
- User approves on gateway UI or control channel
- Approved senders stored in config

**Allowlists**:
- Per-channel sender allowlist
- Phone numbers, usernames, or IDs
- Configured in `channels.<provider>.allowFrom`

**Group Gating**:
- Groups require mention or keyword to respond
- Configured in `channels.<provider>.groups`
- Prevents spam in large groups

### 9.4 Tool Execution Security

**Tool Policy**:
- Deny list: Block specific tools
- Allow list: Allow only specific tools
- Configured in `tools.policy`

**Sandboxing**:
- Optional per-workspace sandbox
- Chroot to workspace directory
- Restrict file access outside workspace
- Network isolation (future)

**Exec Guard Patch**:
- Wraps `exec` and `bash` tools
- Blocks commands with dangerous patterns
- User can override with approval

### 9.5 Credential Storage

**Messaging Provider Credentials**:
- Stored in `~/.openclaw/credentials/<provider>/`
- WhatsApp: `auth-state.json` (Baileys session)
- Telegram: Bot token in config
- Discord: Bot token in config
- Slack: OAuth token in config

**LLM API Keys**:
- Stored in `~/.openclaw/credentials/anthropic/api-key.txt`
- Or environment variable `ANTHROPIC_API_KEY`

**Encryption** (optional):
- Credentials can be encrypted at rest
- Encryption key derived from user password
- Requires password on gateway startup

### 9.6 Network Security

**TLS Support**:
- Optional TLS for WebSocket connections
- Configured with cert and key files
- Certificate pinning for client validation

**Firewall Recommendations**:
- Block gateway port from public internet
- Allow only local network or VPN
- Use Tailscale or WireGuard for remote access

---

## 10. Session Management

### 10.1 Session Lifecycle

```
1. Inbound message arrives
   ↓
2. Router derives session key from message
   ↓
3. Check if session exists in index
   ↓ (if not exists)
4. Create new session entry
5. Initialize empty transcript JSONL
   ↓
6. Load session transcript
   ↓
7. Execute agent turn
   ↓
8. Persist updated transcript
   ↓
9. Update session index with metadata
   ↓
10. Check reset conditions (daily, idle)
    ↓ (if reset due)
11. Archive old transcript
12. Create new session entry
```

### 10.2 Session Key Derivation

**Format**: `agent:<agentId>:<scopeKey>`

**Scope Key Rules**:

| DM Scope Mode | Scope Key | Example |
|---------------|-----------|---------|
| `main` | `main` | `agent:main:main` |
| `per-peer` | `<provider>:<peerId>` | `agent:main:whatsapp:+15551234567` |
| `per-channel-peer` | `<channel>:<provider>:<peerId>` | `agent:main:whatsapp:whatsapp:+15551234567` |
| `per-account-channel-peer` | `<account>:<channel>:<provider>:<peerId>` | `agent:main:default:whatsapp:whatsapp:+15551234567` |

**Group Chat**:
- Format: `agent:<agentId>:<channel>:group:<groupId>`
- Example: `agent:main:discord:group:123456789`

**Thread**:
- Format: `agent:<agentId>:<channel>:thread:<threadId>`
- Example: `agent:main:slack:thread:T123:C456:1234567890.123456`

**Cron**:
- Format: `cron:<jobId>`
- Example: `cron:daily-backup`

**Webhook**:
- Format: `hook:<hookId>`
- Example: `hook:uuid-1234-5678-abcd`

### 10.3 Identity Linking

**Purpose**: Link multiple identities into the same session

**Configuration**:
```json5
{
  session: {
    identityLinks: {
      "user1": [
        "whatsapp:+15551234567",
        "telegram:@alice",
        "discord:123456789"
      ]
    }
  }
}
```

**Effect**: All messages from linked identities share the same session

### 10.4 Session Reset Policies

**Daily Reset**:
- Reset at configured hour (default 4 AM)
- Archives old transcript
- Starts fresh session

**Idle Timeout**:
- Reset after N minutes of inactivity
- Configured in `session.reset.idleMinutes`
- Checks last message timestamp

**Manual Reset**:
- User triggers reset via command or API
- Immediate effect

**Reset Action**:
1. Move old transcript to archive directory
2. Delete session entry from index
3. Next message creates new session

### 10.5 Context Window Management

**Pre-LLM Pruning**:
- Before each agent turn, prune old tool results
- Keep recent messages (configurable limit)
- Summarize truncated history if needed

**Token Counting**:
- Track input/output/context tokens per session
- Stored in session index
- Useful for cost tracking and analytics

**Group Chat History**:
- Include last N messages from group
- Configured in `messages.groupChat.historyLimit`
- Provides context for multi-party conversations

---

## 11. Message Routing & Queuing

### 11.1 Routing Algorithm

```
function route(inboundMessage: InboundMessage): AgentId {
  // 1. Check exact peer binding
  for agent in config.agents.list:
    if agent.bindings.peers[message.provider].includes(message.peerId):
      return agent.id

  // 2. Check guild/team binding (for Discord/Slack)
  for agent in config.agents.list:
    if message.chatType == "group":
      if agent.bindings.guilds[message.provider].includes(message.guildId):
        return agent.id

  // 3. Check account binding (multi-account)
  for agent in config.agents.list:
    if agent.bindings.accounts[message.provider].includes(message.accountId):
      return agent.id

  // 4. Check channel binding
  for agent in config.agents.list:
    if agent.bindings.channels.includes(message.provider):
      return agent.id

  // 5. Default agent
  return config.agents.list[0].id
}
```

### 11.2 Message Deduplication

**Purpose**: Skip duplicate messages from platform retries

**Implementation**:
- In-memory cache of recent message IDs
- TTL: 5 minutes
- Key: `<provider>:<messageId>`

**Algorithm**:
```
function deduplicate(message: InboundMessage): boolean {
  key = `${message.provider}:${message.messageId}`
  if cache.has(key):
    return false  // Duplicate, skip
  cache.set(key, true, ttl=5min)
  return true  // New message
}
```

### 11.3 Message Debouncing

**Purpose**: Batch rapid messages into single agent run

**Configuration**:
```json5
{
  messages: {
    inbound: {
      debounceMs: 2000,
      byChannel: {
        whatsapp: { debounceMs: 3000 },
        telegram: { debounceMs: 1000 }
      }
    }
  }
}
```

**Algorithm**:
```
function debounce(message: InboundMessage):
  key = sessionKey(message)
  timer = debounceTimers[key]

  if timer:
    timer.cancel()
    queuedMessages[key].push(message)
  else:
    queuedMessages[key] = [message]

  debounceTimers[key] = setTimeout(() => {
    messages = queuedMessages[key]
    combined = combineMessages(messages)
    enqueue(combined, key)
    delete debounceTimers[key]
    delete queuedMessages[key]
  }, debounceMs)
```

### 11.4 Queue Management

**Lane-Aware FIFO Queue**:
```
Queues:
  session:agent:main:main → [msg1, msg2]
  session:agent:main:discord:group:123 → [msg3]
  main → [msg4]

Lane Capacity:
  session:* → 1 (serial)
  main → 4 (parallel)
  cron → 2 (parallel)
```

**Enqueue**:
```
function enqueue(message, sessionKey):
  lane = `session:${sessionKey}`
  queue[lane].push(message)
  if queue[lane].running < capacity[lane]:
    dequeue(lane)
```

**Dequeue**:
```
function dequeue(lane):
  if queue[lane].isEmpty():
    return

  message = queue[lane].shift()
  queue[lane].running++

  try:
    runAgent(message, sessionKey)
  finally:
    queue[lane].running--
    dequeue(lane)  // Process next in queue
```

### 11.5 Queue Modes

**Collect** (default):
- Batch queued messages into single followup
- Useful for rapid multi-line messages

**Steer**:
- Inject into current run (skip pending tool calls)
- Useful for urgent corrections

**Followup**:
- Queue as separate turns
- Useful for distinct questions

**Interrupt**:
- Abort current run, execute new message
- Useful for emergencies

**Configuration**:
```json5
{
  messages: {
    queue: {
      mode: "collect",
      debounceMs: 1000
    }
  }
}
```

### 11.6 Overflow Policies

**Cap**: Max queued messages per session (default 20)

**Drop Policies**:
- `old`: Drop oldest queued message
- `new`: Drop newest incoming message
- `summarize`: Summarize queued messages into one

**Configuration**:
```json5
{
  messages: {
    queue: {
      cap: 20,
      drop: "old"
    }
  }
}
```

---

## 12. Tool Execution System

### 12.1 Tool Interface

```typescript
interface Tool {
  name: string
  description: string
  schema: JSONSchema
  invoke(input: unknown, context: ToolContext): Promise<ToolResult>
}

interface ToolContext {
  agentId: string
  sessionKey: string
  workspace: string
  channel?: string
  user?: {
    id: string
    name?: string
    provider: string
  }
}

interface ToolResult {
  success: boolean
  output?: string
  error?: string
  metadata?: Record<string, unknown>
}
```

### 12.2 Built-In Tools

**File Operations**:
- `read`: Read file contents
- `write`: Write file contents
- `edit`: Edit file with search/replace
- `glob`: Find files by pattern
- `grep`: Search file contents by regex

**System**:
- `exec`: Execute shell command (with optional sandboxing)
- `bash`: Execute bash script

**Browser**:
- `browser.snapshot`: Take screenshot of URL
- `browser.action`: Click, type, scroll on page
- `browser.upload`: Upload file to page

**Canvas**:
- `canvas.create`: Create new canvas UI
- `canvas.update`: Update canvas content
- `canvas.render`: Render canvas to HTML

**Session Management**:
- `sessions.list`: List all sessions
- `sessions.get`: Get session details
- `sessions.patch`: Update session metadata
- `sessions.reset`: Reset session transcript

**Gateway Operations**:
- `node.invoke`: Invoke node command (iOS/Android/macOS app)
- `channels.status`: Get channel connection status
- `config.get`: Get configuration value
- `config.set`: Set configuration value

**Cron**:
- `cron.list`: List cron jobs
- `cron.create`: Create new cron job
- `cron.delete`: Delete cron job

### 12.3 Channel-Specific Tools

**WhatsApp**:
- `whatsapp.send`: Send message (with media, reactions, etc.)
- `whatsapp.groups`: List groups
- `whatsapp.status`: Post status update

**Telegram**:
- `telegram.send`: Send message (with inline keyboard, etc.)
- `telegram.pin`: Pin message
- `telegram.restrict`: Restrict user in group

**Discord**:
- `discord.send`: Send message (with embeds, buttons, etc.)
- `discord.embed`: Create rich embed
- `discord.role`: Assign role to user

**Slack**:
- `slack.send`: Send message (with blocks, etc.)
- `slack.upload`: Upload file
- `slack.pin`: Pin message

### 12.4 Tool Schema Validation

**JSON Schema** (OpenAPI-compatible):
```json
{
  "name": "read",
  "description": "Read a file from the filesystem",
  "input_schema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Absolute path to the file"
      },
      "offset": {
        "type": "number",
        "description": "Line number to start reading from"
      },
      "limit": {
        "type": "number",
        "description": "Number of lines to read"
      }
    },
    "required": ["file_path"]
  }
}
```

**Validation**:
- Validate tool input against schema before invocation
- Return error if validation fails
- Prevents malformed tool calls from breaking agent

### 12.5 Tool Policy & Sandboxing

**Policy Configuration**:
```json5
{
  tools: {
    policy: {
      deny: ["exec", "bash"],  // Block these tools
      allow: ["*"]             // Allow all others
    }
  }
}
```

**Sandbox Configuration**:
```json5
{
  agents: {
    defaults: {
      sandbox: {
        enabled: true,
        workspaceRoot: "/tmp/sandbox"
      }
    }
  }
}
```

**Sandbox Behavior**:
- Chroot to workspace directory
- File operations restricted to workspace
- Exec commands run in isolated environment
- Network access (future enhancement)

### 12.6 Tool Execution Flow

```
1. LLM generates tool use block
   ↓
2. Agent runtime extracts tool name and input
   ↓
3. Validate input against tool schema
   ↓ (if invalid)
4. Return validation error to LLM
   ↓ (if valid)
5. Check tool policy (deny/allow)
   ↓ (if denied)
6. Return policy error to LLM
   ↓ (if allowed)
7. Invoke tool handler with input and context
   ↓
8. Tool executes (may spawn subprocess)
   ↓
9. Tool returns result (success or error)
   ↓
10. Serialize result to tool result block
   ↓
11. Continue agent loop with tool result
```

---

## 13. Extension & Plugin Architecture

### 13.1 Plugin Types

1. **Channel Providers**: Add new messaging platforms
2. **Tool Providers**: Add new tools
3. **Skill Packages**: Add agent skills
4. **Model Providers**: Add LLM providers
5. **Middleware**: Hook into lifecycle events

### 13.2 Plugin Structure

**Directory**: `extensions/<plugin-name>/`

**Package.json**:
```json
{
  "name": "@openclaw/msteams",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "openclaw": {
    "type": "channel",
    "provider": "msteams"
  },
  "dependencies": {
    "@microsoft/teams": "^2.0.0"
  },
  "devDependencies": {
    "openclaw": "workspace:*"
  }
}
```

**Entry Point** (`src/index.ts`):
```typescript
import { ChannelProvider } from 'openclaw/plugin-sdk'

export default class MSTeamsProvider implements ChannelProvider {
  async initialize() {
    // Initialize Teams connection
  }

  async shutdown() {
    // Cleanup
  }

  getStatus() {
    return { status: 'connected', accounts: [...] }
  }

  onInboundMessage(handler) {
    // Listen for Teams messages
    // Call handler(inboundMessage) for each message
  }

  async sendMessage(params) {
    // Send message via Teams API
  }
}
```

### 13.3 Plugin Discovery & Loading

**Discovery**:
1. Scan `extensions/` directory
2. Check `~/.openclaw/plugins/` directory
3. Check bundled plugins in core

**Loading**:
1. Read `package.json` to identify plugin type
2. Import entry point module (dynamic import)
3. Validate plugin exports interface
4. Register plugin with gateway

**Activation**:
1. User enables plugin in config
2. Gateway initializes plugin on startup
3. Plugin appears in channel list or tool list

### 13.4 Plugin SDK

**Exports**:
```typescript
// openclaw/plugin-sdk

export interface ChannelProvider { ... }
export interface Tool { ... }
export interface SkillPackage { ... }
export interface ModelProvider { ... }

export type InboundMessage = { ... }
export type SendParams = { ... }
export type ToolContext = { ... }
```

**Utilities**:
```typescript
export function createLogger(name: string): Logger
export function loadConfig(path: string): Config
export function emitEvent(event: string, payload: any): void
```

### 13.5 Security Considerations

**Untrusted Plugins**:
- Plugins run in same process as gateway (high trust)
- Avoid loading untrusted plugins
- Verify plugin signature before loading (future)

**Sandboxing**:
- Future: Run plugins in separate process
- Communication via IPC (stdio or WebSocket)
- Restricted filesystem access

---

## 14. Deployment Models

### 14.1 Local Gateway (Default)

**Architecture**:
- Gateway runs on user's local machine
- Clients connect via loopback (127.0.0.1)
- All data stays on device

**Use Cases**:
- Personal use
- Development
- Maximum privacy

**Setup**:
```bash
openclaw gateway run --bind loopback --port 18789
```

### 14.2 Tailscale Gateway

**Architecture**:
- Gateway runs on any device
- Clients connect via Tailscale VPN
- Secure mesh network

**Use Cases**:
- Multi-device access
- Remote access without exposing public IP
- Home server deployment

**Setup**:
```bash
# On gateway device
tailscale up
openclaw gateway run --bind tailnet --port 18789

# On client device
tailscale up
openclaw config set gateway.url ws://gateway-device:18789
```

### 14.3 Remote Gateway

**Architecture**:
- Gateway runs on VPS or cloud VM
- Clients connect over public internet
- TLS + authentication required

**Use Cases**:
- Always-on gateway
- Multiple users (family/team)
- High availability

**Setup**:
```bash
# On gateway server
openclaw gateway run --bind 0.0.0.0 --port 18789 \
  --tls-cert /path/to/cert.pem \
  --tls-key /path/to/key.pem \
  --auth-token <secret>

# On client device
openclaw config set gateway.url wss://gateway.example.com:18789
openclaw config set gateway.auth.token <secret>
```

### 14.4 macOS App (Menubar)

**Architecture**:
- Gateway embedded in macOS app
- Runs in background as menubar app
- Native UI for status and control

**Features**:
- Auto-start on login
- System tray icon with status
- Quick access to logs and settings
- Integrated channel pairing

**Setup**:
- Download `.dmg` from website
- Drag to Applications folder
- Launch app, grant permissions
- Gateway starts automatically

### 14.5 Docker Deployment

**Dockerfile**:
```dockerfile
FROM node:22-alpine
RUN npm install -g openclaw@latest
VOLUME /root/.openclaw
EXPOSE 18789
CMD ["openclaw", "gateway", "run", "--bind", "0.0.0.0"]
```

**Docker Compose**:
```yaml
services:
  openclaw:
    image: openclaw/openclaw:latest
    volumes:
      - ./data:/root/.openclaw
    ports:
      - "18789:18789"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

**Setup**:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## 15. Implementation Guidelines

### 15.1 Language Considerations

**Recommended Languages**:
- **Go**: Excellent concurrency, single binary, fast startup
- **Rust**: Memory safety, performance, strong typing
- **TypeScript/Node.js**: Reference implementation, rich ecosystem
- **Python**: Rapid development, AI/ML libraries
- **C#/.NET**: Cross-platform, strong typing, async/await

**Key Requirements**:
- WebSocket server with text frames
- JSON parsing and serialization
- Async I/O for concurrent connections
- HTTP client for external APIs
- Process management for tool execution
- File I/O for session storage

### 15.2 Architecture Recommendations

**Gateway**:
- Single-process architecture (easier deployment)
- Async/await for concurrency (avoid threads if possible)
- Event-driven message handling
- In-memory queue for run management
- Filesystem for persistent state

**Agent Runtime**:
- Embedded in gateway process (not RPC)
- Streaming response handling
- Tool execution with timeout
- Context window management

**Channel Connectors**:
- Separate module per provider
- Consistent interface (ChannelProvider)
- Retry logic with exponential backoff
- Rate limiting to respect API limits

### 15.3 Testing Strategy

**Unit Tests**:
- Test each component in isolation
- Mock external dependencies (API clients)
- Cover edge cases (empty messages, long text, etc.)

**Integration Tests**:
- Test gateway + agent + channel end-to-end
- Use test messaging accounts
- Verify session persistence

**E2E Tests**:
- Test full workflow (message → agent → response)
- Use Docker for reproducible environment
- Simulate multiple clients

### 15.4 Performance Optimization

**Concurrency**:
- Process multiple sessions in parallel (limited by maxConcurrent)
- Single session runs serially (avoid race conditions)

**Memory**:
- Stream large responses (don't buffer in memory)
- Prune old tool results before LLM call
- Lazy-load session transcripts

**Network**:
- Reuse HTTP connections (keep-alive)
- Batch outbound messages when possible
- Compress large payloads

**Disk**:
- Append-only JSONL for fast writes
- Index file for fast session lookup
- Archive old transcripts to reduce disk usage

### 15.5 Error Handling

**Transient Errors** (retry):
- Network timeouts
- Rate limit errors
- Temporary API failures

**Permanent Errors** (report):
- Invalid API keys
- Malformed messages
- Schema validation errors

**Graceful Degradation**:
- Continue running if one channel fails
- Skip failed tool executions (return error to LLM)
- Log errors but don't crash gateway

### 15.6 Logging & Monitoring

**Log Levels**:
- `trace`: Very verbose (protocol details)
- `debug`: Debug info (tool calls, routing)
- `info`: Informational (connections, runs)
- `warn`: Warnings (retries, skipped messages)
- `error`: Errors (failures, crashes)
- `silent`: No logs

**Metrics** (optional):
- Message throughput (messages/sec)
- Agent run duration (latency)
- Token usage (cost tracking)
- Error rate (failures/total)

**Health Checks**:
- Gateway uptime
- Channel connection status
- Queue depth
- Memory usage

### 15.7 Configuration Management

**File Format**: JSON5 (allows comments)

**Location**: `~/.openclaw/openclaw.json`

**Hot Reload**:
- Watch config file for changes
- Reload without restarting gateway
- Notify connected clients of config changes

**Validation**:
- Validate config on load
- Report errors clearly
- Provide defaults for missing values

### 15.8 Deployment Checklist

- [ ] Install runtime (Node.js, Go, etc.)
- [ ] Install OpenClaw binary
- [ ] Create config file
- [ ] Set up LLM API keys
- [ ] Configure channels (bot tokens, etc.)
- [ ] Start gateway daemon
- [ ] Verify connectivity (`openclaw channels status`)
- [ ] Test message flow (send test message)
- [ ] Set up auto-start (systemd, launchd, etc.)
- [ ] Configure firewall (block public access if local)
- [ ] Set up monitoring (logs, metrics)

---

## Conclusion

This specification provides a complete blueprint for reimplementing OpenClaw in any programming language. Key takeaways:

1. **Gateway-Agent Separation**: Gateway maintains all provider connections; agent runtime is embedded for simplicity
2. **Session Isolation**: Each conversation is independent with its own transcript
3. **Lane-Based Queuing**: Serialize per-session, parallelize across sessions
4. **Stream-First**: Real-time response chunks with platform-aware chunking
5. **Tool-Oriented**: Everything is a tool; extensible through plugins
6. **Local-First**: All data stays on user's device; no cloud dependency

For implementation questions or clarifications, refer to the reference TypeScript implementation at https://github.com/openclaw/openclaw.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-30
**Author**: Claude (Anthropic PBC)
**License**: MIT
