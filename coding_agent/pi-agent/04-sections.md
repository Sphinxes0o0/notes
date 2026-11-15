---
title: "5. 关键文件索引"
---

# 5. 关键文件索引 {#chapter}

[返回总目录](../pi-agent)

### 5. 关键文件索引 {#_5-关键文件索引}

| 组件 | 关键文件 |
|------|---------|
| **pi_agent_rust 两阶段 enforcement** | `src/extensions.rs` (~2010, 4331-4400, 9933, 10050-10145), `src/extension_dispatcher.rs` (~2795-2865) |
| **pi_agent_rust hashline_edit** | `src/tools.rs` (~7300-7722) |
| **oh-my-pi hashline** | `packages/hashline/src/{format,patcher,recovery,snapshots}.ts` |
| **oh-my-pi BM25 tool discovery** | `packages/coding-agent/src/tool-discovery/tool-index.ts`, `src/tools/search-tool-bm25.ts` |
| **oh-my-pi LSP** | `packages/coding-agent/src/lsp/{client,index}.ts` |
| **oh-my-pi DAP** | `packages/coding-agent/src/dap/{client,session}.ts` |
## 定制深化 {#定制深化}

### 1. 自定义扩展完整示例 (TypeScript) {#_1-自定义扩展完整示例-typescript}

以下是一个完整的 PI Agent 扩展，实现一个带生命周期管理的自定义工具——文件内容校验和计算器。

```typescript
// my-checksum-extension/src/index.ts
import type {
  Extension,
  Tool,
  ToolContext,
  LifecycleHook,
  LifecycleHooks,
} from '@earendil-works/pi-agent-core';
import crypto from 'crypto';
import fs from 'fs/promises';

// --- Tool Definition ---

interface ChecksumResult {
  file: string;
  algorithm: string;
  hash: string;
  bytes: number;
}

interface ChecksumParams {
  path: string;
  algorithm?: 'sha256' | 'sha512' | 'md5';
}

const checksumTool: Tool<ChecksumParams, ChecksumResult> = {
  name: 'checksum',
  description: 'Compute a cryptographic checksum of a file',

  // JSON Schema for parameter validation
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Absolute path to the file' },
      algorithm: {
        type: 'string',
        enum: ['sha256', 'sha512', 'md5'],
        default: 'sha256',
        description: 'Hash algorithm to use',
      },
    },
    required: ['path'],
  },

  // Lifecycle: called once when extension loads
  onLoad?: async (ctx: ToolContext) => {
    console.log('[checksum] extension loaded');
    ctx.registerConfig({
      algorithm: { type: 'string', default: 'sha256' },
    });
  },

  // Lifecycle: called before each invocation
  async beforeInvoke(params: ChecksumParams): Promise<void> {
    const stat = await fs.stat(params.path).catch(() => null);
    if (!stat) throw new Error(`File not found: ${params.path}`);
    if (!stat.isFile()) throw new Error(`Not a file: ${params.path}`);
  },

  // Core execution
  async execute(params: ChecksumParams, ctx: ToolContext): Promise<ChecksumResult> {
    const algorithm = params.algorithm ?? ctx.getConfig?.('algorithm') ?? 'sha256';
    const fileBuffer = await fs.readFile(params.path);
    const hash = crypto.createHash(algorithm).update(fileBuffer).digest('hex');

    return {
      file: params.path,
      algorithm,
      hash,
      bytes: fileBuffer.length,
    };
  },

  // Lifecycle: called after successful execution
  async afterInvoke?(result: ChecksumResult): Promise<void> {
    ctx.getLog?.().info(`[checksum] ${result.algorithm} = ${result.hash}`);
  },

  // Lifecycle: called on extension unload
  onUnload?: () => void | Promise<void> {
    console.log('[checksum] extension unloaded');
  },
};

// --- Extension Entry Point ---

const extension: Extension = {
  name: 'my-checksum',
  version: '1.0.0',
  tools: [checksumTool],

  // Lifecycle hooks
  hooks: {
    onAgentStart: async (ctx) => {
      ctx.getLog?.().info('[checksum] agent started');
    },
    onToolCall: async (toolName, params, result) => {
      if (toolName === 'checksum') {
        ctx.getLog?.().debug(`[checksum] called with params:`, params);
      }
    },
    onAgentEnd: async () => {
      console.log('[checksum] agent session ended');
    },
  } satisfies Partial<LifecycleHooks>,

  // Optional: declare dependencies
  dependencies: [],

  // Optional: capability declarations for sandboxing
  capabilities: ['fs:read', 'crypto'],
};

export default extension;

// --- Package manifest (package.json) ---
// {
//   "name": "my-checksum-extension",
//   "main": "dist/index.js",
//   "type": "module",
//   "peerDependencies": {
//     "@earendil-works/pi-agent-core": "^2.x"
//   }
// }
```

**生命周期时序:**

```
Extension Load
    │
    ▼
onLoad() → registerConfig()
    │
    ▼
Agent Start → onAgentStart()
    │
    ▼
Tool Call ──→ beforeInvoke() ──→ execute() ──→ afterInvoke()
    │                                     │
    └───────── error ─────────────────────┘
    │
    ▼
onToolCall() hook (per call)
    │
    ▼
Agent End → onAgentEnd()
    │
    ▼
onUnload()
```

**安装与使用:**

```bash
npm install -g --ignore-scripts my-checksum-extension
# 或本地开发
npm link  # 在扩展目录中运行
pi-agent  # 启动交互模式
```

Agent 内调用: `checksum { "path": "/etc/hosts", "algorithm": "sha256" }`

---

### 2. 自定义 Provider 实现

添加一个新的 LLM Provider——以 Cloudflare Workers AI 为例。

```typescript
// providers/cloudflare-ai.ts
import {
  createProvider,
  type Provider,
  type ChatMessage,
  type ChatCompletionResponse,
  type StreamChunk,
} from '@earendil-works/pi-ai';

interface CloudflareAIConfig {
  accountId: string;
  apiKey: string;
  baseUrl?: string; // 默认 https://api.cloudflare.com/client/v4
}

interface CloudflareAIResponse {
  result: {
    response: string;
    metadata?: {
      tokensUsed?: number;
      model?: string;
    };
  };
  success: boolean;
  errors?: string[];
}

// Provider 实现
export const cloudflareAIProvider: Provider<CloudflareAIConfig> = {
  name: 'cloudflare-ai',
  displayName: 'Cloudflare Workers AI',

  // 支持的模型列表
  models: [
    { id: '@cf/meta/llama-3-8b-instruct', name: 'Llama 3 8B' },
    { id: '@cf/meta/llama-3-70b-instruct', name: 'Llama 3 70B' },
    { id: '@cf/google/gemma-7b-instruct', name: 'Gemma 7B' },
    { id: '@cf/mistral/mistral-7b-instruct-v0.1', name: 'Mistral 7B' },
    { id: '@cf/openchat/openchat-7b-v3.1', name: 'OpenChat 7B' },
  ],

  // 默认模型
  defaultModel: '@cf/meta/llama-3-8b-instruct',

  // OAuth / API Key 认证方式
  auth: {
    type: 'api-key',
    header: 'Authorization',
    prefix: 'Bearer',
    envVar: 'CLOUDFLARE_API_KEY',
  },

  // 构建请求
  buildRequest: (config: CloudflareAIConfig, model: string, messages: ChatMessage[]) => {
    const url = `https://api.cloudflare.com/client/v4/accounts/${config.accountId}/ai/${model}`;
    return {
      url,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: {
        messages: messages.map(m => ({
          role: m.role,
          content: m.content,
        })),
        // Cloudflare 特定参数
        stream: false,
        max_tokens: 4096,
      },
    };
  },

  // 解析响应
  parseResponse: (response: CloudflareAIResponse): ChatCompletionResponse => {
    if (!response.success) {
      throw new Error(`Cloudflare AI error: ${response.errors?.join(', ')}`);
    }
    return {
      content: response.result.response,
      model: response.result.metadata?.model ?? 'unknown',
      usage: {
        inputTokens: 0, // Cloudflare 不总是返回 token 数
        outputTokens: response.result.metadata?.tokensUsed ?? 0,
      },
      finishReason: 'stop',
    };
  },

  // 流式响应解析 (SSE 格式)
  parseStreamChunk: (chunk: string): StreamChunk | null => {
    // Cloudflare SSE 格式: data: {"response":"Hello"}
    if (!chunk.startsWith('data: ')) return null;
    try {
      const data = JSON.parse(chunk.slice(6));
      return {
        delta: data.response ?? '',
        done: false,
      };
    } catch {
      return null;
    }
  },

  // 错误处理映射
  errorMap: {
    401: 'Invalid Cloudflare API key',
    403: 'Account ID or permissions error',
    429: 'Rate limited — try a smaller model or wait',
    500: 'Cloudflare AI service error',
    503: 'Cloudflare AI temporarily unavailable',
  },
};

// 注册 Provider
export function registerCloudflareAI() {
  return createProvider(cloudflareAIProvider);
}

// 使用示例:
// const ai = createAI({
//   provider: 'cloudflare-ai',
//   model: '@cf/meta/llama-3-8b-instruct',
//   config: {
//     accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
//     apiKey: process.env.CLOUDFLARE_API_KEY!,
//   },
// });
```

**Provider 注册流程:**

```typescript
// 在你的扩展或配置中注册
import { registerProvider } from '@earendil-works/pi-ai';

registerProvider('cloudflare-ai', cloudflareAIProvider);

// 模型选择通过 config
const ai = createAI({
  provider: 'cloudflare-ai',
  model: '@cf/google/gemma-7b-instruct',
  config: {
    accountId: 'your-account-id',
    apiKey: 'your-api-key',
  },
});
```

---

### 3. oh-my-pi 双内核架构 (Rust + Bun) {#_3-oh-my-pi-双内核架构-rust-bun}

oh-my-pi 的核心创新是同时运行两个持久化内核——Python 和 Bun——它们可以**直接调用 Agent 工具**，无需进程间通信开销。

#### 架构概览 {#架构概览}

```
┌─────────────────────────────────────────────────────┐
│                    oh-my-pi Core (Rust)              │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Agent   │  │  Tool    │  │   Kernel Manager │  │
│  │  Engine  │──│  Registry│──│                   │  │
│  └──────────┘  └──────────┘  └────────┬─────────┘  │
│                                       │             │
│                    IPC (mpsc channel) │             │
│                                ┌──────┴──────┐      │
│                                │             │      │
│                     ┌──────────▼──┐  ┌──────▼────┐  │
│                     │ Python Kernel│  │ Bun Kernel │  │
│                     │  (PyO3/mijo) │  │  (Bun API) │  │
│                     └──────┬───────┘  └──────┬─────┘  │
│                            │                 │        │
│                     ┌──────▼─────────────────▼────┐  │
│                     │   Tool Calling Bridge        │  │
│                     │  (kernel.invoke_tool)        │  │
│                     └─────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 内核工具调用协议 {#内核工具调用协议}

每个内核通过 Rust 提供的 `invoke_tool` FFI 绑定调用 Agent 工具：

```rust
// src/kernel/mod.rs

// 内核调用工具的通用接口
pub trait KernelBridge {
    fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> impl Future<Output = Result<serde_json::Value, KernelError>> + Send;
}

// Python 内核实现 (使用 PyO3)
pub struct PythonKernel {
    interpreter: PythonInterpreter,
    tool_bridge: ToolBridge,
}

impl KernelBridge for PythonKernel {
    async fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, KernelError> {
        // 获取工具元数据
        let tool_meta = self.tool_bridge.get_tool_meta(tool_name)?;
        
        // 在 Python 侧执行工具
        let result = self.interpreter
            .call(
                "agent",
                "invoke_tool",
                (tool_name, params, tool_meta),
            )
            .await?;
        
        Ok(result)
    }
}

// Bun 内核实现 (使用 NAPI)
pub struct BunKernel {
    napi_env: NapiEnv,
    tool_bridge: ToolBridge,
}

impl KernelBridge for BunKernel {
    async fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, KernelError> {
        let promise = self.napi_env
            .call_async("agent", "invokeTool", tool_name, params)?;
        
        promise.await
    }
}
```

#### Python 内核中的工具调用 {#python-内核中的工具调用}

```python
# python/agent.py
import asyncio
import json
from typing import Any

class AgentBridge:
    """Python 内核调用的桥梁"""
    
    def __init__(self, kernel):
        self.kernel = kernel  # PyO3 Rust 绑定
        self._tool_registry: dict[str, callable] = {}
    
    def register_tool(self, name: str, handler: callable):
        self._tool_registry[name] = handler
    
    async def invoke_tool(self, tool_name: str, params: dict, meta: dict) -> Any:
        """由 Rust 内核调用此方法，再转发给实际工具"""
        if tool_name not in self._tool_registry:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self._tool_registry[tool_name]
        
        # 支持异步工具
        if asyncio.iscoroutinefunction(handler):
            return await handler(**params)
        return handler(**params)

# 内置 ripgrep 工具 (Python 实现)
async def grep(path: str, pattern: str, context: int = 3, 
               case_sensitive: bool = False) -> list[dict]:
    """内置 ripgrep，通过 Rust 侧重定向到 subprocess 或 native 实现"""
    result = await AgentBridge.instance().kernel.rpc(
        "tool://grep",
        path=path,
        pattern=pattern,
        context=context,
        case_sensitive=case_sensitive
    )
    return result

# 注册工具
agent_bridge.register_tool("grep", grep)
```

#### Bun 内核中的工具调用 {#bun-内核中的工具调用}

```typescript
// bun/kernel/agent.ts

// Bun 内核通过 NAPI 调用 Rust 工具
const rust = require('oh_my_pi_native') as typeof import('oh-my-pi-native');

class AgentBridge {
  private static instance: AgentBridge;
  
  private constructor() {}
  
  static getInstance(): AgentBridge {
    if (!AgentBridge.instance) {
      AgentBridge.instance = new AgentBridge();
    }
    return AgentBridge.instance;
  }
  
  // 调用注册的工具
  async invokeTool(toolName: string, params: Record<string, unknown>): Promise<unknown> {
    const tool = this.getTool(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }
    return tool.handler(params);
  }
  
  // 内置 glob 工具 (Bun 实现)
  async glob(pattern: string, cwd: string = process.cwd()): Promise<string[]> {
    // Bun.glob 是原生实现，比 Node glob 快 10x
    return Array.from(
      new Bun.Glob(pattern).scanSync({ cwd, onlyFiles: true })
    );
  }
  
  // 内置文件读写 (直接调用 Rust 而非 Bun 原生)
  async readFile(path: string): Promise<string> {
    return rust.fs.readFile(path, 'utf-8');
  }
  
  async writeFile(path: string, content: string): Promise<void> {
    return rust.fs.writeFile(path, content);
  }
}

// 导出供 Rust NAPI 调用
(globalThis as any).agentBridge = AgentBridge.getInstance();
```

#### 内核间通信 {#内核间通信}

```rust
// src/ipc/mod.rs

use tokio::sync::mpsc;

// 内核间消息格式
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
#[serde(tag = "type", content = "payload")]
pub enum KernelMessage {
    // Python -> Bun
    PythonExec { code: String, id: u64 },
    PythonResult { id: u64, result: serde_json::Value },
    
    // Bun -> Python  
    BunExec { code: String, id: u64 },
    BunResult { id: u64, result: serde_json::Value },
    
    // 工具调用转发
    ToolCall { from: KernelId, tool: String, params: serde_json::Value },
    ToolResult { to: KernelId, id: u64, result: serde_json::Value },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum KernelId {
    Python,
    Bun,
    Rust,  // 主控 Rust 进程
}

// IPC 通道
pub struct IpcChannel {
    sender: mpsc::Sender<KernelMessage>,
    receiver: mpsc::Receiver<KernelMessage>,
}

impl IpcChannel {
    pub fn new(capacity: usize) -> (Self, Self) {
        let (tx1, rx2) = mpsc::channel(capacity);
        let (tx2, rx1) = mpsc::channel(capacity);
        (Self { sender: tx1, receiver: rx1 }, Self { sender: tx2, receiver: rx2 })
    }
    
    pub async fn send(&self, msg: KernelMessage) {
        self.sender.send(msg).await.expect("channel closed");
    }
    
    pub async fn recv(&mut self) -> Option<KernelMessage> {
        self.receiver.recv().await
    }
}
```

**关键设计决策:**

| 方面 | 决策 | 原因 |
|------|------|------|
| 持久化内核 | Python/Bun 常驻内存 | 避免冷启动开销，Python 库初始化慢 |
| 工具调用 | Rust 作为仲裁者 | 内核本身不可信，防止注入攻击 |
| 原生重实现 | ripgrep/glob 等用 Rust 重写 | subprocess 启动 5-50ms，native <1ms |
| AST 编辑 | Hashline 锚定 | 并发编辑时防止行号错位 |

---
