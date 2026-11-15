---
title: "2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors）"
description: "2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors）的内容说明与阅读参考。"
---

# 2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors） {#chapter}

[返回总目录](../pi-agent)

### 2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors） {#_2-oh-my-pi-hashline-编辑机制-content-hashes-as-anchors}

#### 2.1 Hashline 格式 {#_2-1-hashline-格式}

位置：`packages/hashline/src/format.ts`

每个 hunk 以 `¶PATH#HASH` 头部开始：

- `¶`（HL_FILE_PREFIX）标记 section 头部
- `HASH` 是文件内容的 **4 字符 xxHash32 截断**（LF 归一化后计算）
- 通过 `computeFileHash()` 计算（行 90）：

```typescript
export function computeFileHash(text: string): string {
  const normalized = normalizeFileHashText(text);
  const low16 = Bun.hash.xxHash32(normalized, 0) & 0xffff;
  return low16.toString(16).padStart(4, "0");
}
```

**Hunk 内操作**（format.ts 行 8-14）：

```typescript
export const HL_OP_INSERT_BEFORE = "↑";  // 插入到 LINE 之前
export const HL_OP_INSERT_AFTER = "↓";   // 插入到 LINE 之后
export const HL_OP_REPLACE = ":";         // 替换 A..B 行
export const HL_OP_DELETE = "!";          // 删除 A..B 行
```

#### 2.2 Stale Edit 检测 {#_2-2-stale-edit-检测}

位置：`packages/hashline/src/patcher.ts`（行 311-342）

`#applyWithRecovery` 方法在应用前验证哈希：

```typescript
#applyWithRecovery(args): ApplyResult {
  const { section, canonicalPath, exists, normalized, edits, applyOptions } = args;
  const expected = exists ? section.fileHash : undefined;
  if (expected === undefined) return applyEdits(normalized, [...edits], applyOptions);

  const currentHash = computeFileHash(normalized);
  if (currentHash === expected) return applyEdits(normalized, [...edits], applyOptions);

  // 哈希不匹配 → 尝试恢复
  const recovered = this.recovery?.tryRecover({...});
  if (recovered) return recoveryToApplyResult(recovered);

  // 仍不匹配 → 抛出 MismatchError
  throw new MismatchError({
    path: section.path,
    expectedFileHash: expected,
    actualFileHash: currentHash,
    fileLines: normalized.split("\n"),
    anchorLines: section.collectAnchorLines(),
  });
}
```

#### 2.3 三路恢复机制 {#_2-3-三路恢复机制}

位置：`packages/hashline/src/recovery.ts`

当检测到哈希不匹配时，`Recovery` 类尝试三种策略：

1. **Full snapshot 三路合并**（行 148-157）：将编辑应用到缓存的 `fullText`，然后用 `Diff.applyPatch` 合并到当前内容
2. **Session chain replay**（行 155）：若 snapshot 不是 head 且行数匹配，直接重放到当前文本
3. **Sparse overlay 重建**（行 159-161）：从行映射重建文件，验证哈希，然后三路合并

```typescript
tryRecover(args: RecoveryArgs): RecoveryResult | null {
  const head = this.store.head(path);
  const snapshot = this.store.byHash(path, fileHash);

  if (snapshot.fullText !== undefined) {
    const merged = applyEditsToSnapshot(snapshot.fullText, currentText, edits, options, recoveryWarning);
    if (merged !== null) return merged;
    if (isSessionChain) return replaySessionChainOnCurrent(snapshot.fullText, currentText, edits, options);
    return null;
  }
  // 稀疏 snapshot 路径...
}
```

#### 2.4 Snapshot Store {#_2-4-snapshot-store}

位置：`packages/hashline/src/snapshots.ts`

`InMemorySnapshotStore` 维护每个路径的快照历史（每个路径最多 4 个快照，30 个路径 LRU）：

```typescript
export interface Snapshot {
  readonly lines: Map<number, string>;  // 1-indexed line → content
  fullText?: string;                     // 全文件读取
  fileHash?: string;                    // 4-hex 哈希
  recordedAt: number;
}

export class InMemorySnapshotStore extends SnapshotStore {
  readonly #snapshots: LRUCache<string, Snapshot[]>;

  head(path: string): Snapshot | null { ... }
  byHash(path: string, fileHash: string): Snapshot | null { ... }
  recordContiguous(path: string, startLine: number, lines: readonly string[], metadata?: SnapshotMetadata): void { ... }
}
```

Snapshot store 在 `ToolSession` 中接入（`src/edit/file-snapshot-store.ts` 行 19-21）：

```typescript
export function getFileSnapshotStore(session: ToolSession): InMemorySnapshotStore {
  if (!session.fileSnapshotStore) session.fileSnapshotStore = new InMemorySnapshotStore();
  return session.fileSnapshotStore;
}
```

---

### 3. oh-my-pi Tool Discovery（BM25 Search Mid-Session） {#_3-oh-my-pi-tool-discovery-bm25-search-mid-session}

#### 3.1 Hidden Index 架构 {#_3-1-hidden-index-架构}

位置：`packages/coding-agent/src/tool-discovery/tool-index.ts`

BM25 索引从 `DiscoverableTool` 描述符构建：

```typescript
export interface DiscoverableTool {
  name: string;
  label: string;
  summary: string;              // 简短 BM25 语料（描述前 200 字符）
  source: DiscoverableToolSource;  // "builtin" | "mcp" | "extension" | "custom"
  serverName?: string;          // 仅 MCP
  mcpToolName?: string;         // 仅 MCP
  schemaKeys: string[];
}

export interface DiscoverableToolSearchIndex {
  documents: DiscoverableToolSearchDocument[];
  averageLength: number;
  documentFrequencies: Map<string, number>;  // IDF 计算
}
```

#### 3.2 Field Weighting {#_3-2-field-weighting}

位置：tool-index.ts 行 52-59

```typescript
const FIELD_WEIGHTS = {
  name: 6,       // 工具名最高权重
  label: 4,
  mcpToolName: 4,
  serverName: 2,
  summary: 2,
  schemaKey: 1,  // 参数名最低权重
} as const;
```

#### 3.3 Tokenization {#_3-3-tokenization}

位置：tool-index.ts 行 74-93

```typescript
function tokenize(value: string): string[] {
  return value
    .normalize("NFKD")
    .replace(/\p{M}+/gu, "")           // 去除组合标记（重音）
    .replace(/(\p{Lu}+)(\p{Lu}\p{Ll})/gu, "$1 $2")  // ACRONYM 边界
    .replace(/(\p{Ll}|\p{N})(\p{Lu})/gu, "$1 $2")    // camelCase
    .replace(/[^\p{L}\p{N}]+/gu, " ")  // 分隔符
    .toLowerCase()
    .trim()
    .split(/\s+/)
    .filter(token => token.length > 0);
}
```

#### 3.4 BM25 Scoring {#_3-4-bm25-scoring}

位置：tool-index.ts 行 221-256

标准 BM25 公式配合 field weighting：

```typescript
const BM25_K1 = 1.2;
const BM25_B = 0.75;
const BM25_DELTA = 1.0;

export function searchDiscoverableTools(
  index: DiscoverableToolSearchIndex,
  query: string,
  limit: number,
): DiscoverableToolSearchResult[] {
  const queryTokens = tokenize(query);
  // ...
  return index.documents
    .map(document => {
      let score = 0;
      for (const [token, queryTermCount] of queryTermCounts) {
        const termFrequency = document.termFrequencies.get(token) ?? 0;
        if (termFrequency === 0) continue;
        const documentFrequency = index.documentFrequencies.get(token) ?? 0;
        const idf = Math.log(1 + (index.documents.length - documentFrequency + 0.5) / (documentFrequency + 0.5));
        const normalization = BM25_K1 * (1 - BM25_B + BM25_B * (document.length / index.averageLength));
        score += queryTermCount * idf * ((termFrequency * (BM25_K1 + 1)) / (termFrequency + normalization) + BM25_DELTA);
      }
      return { tool: document.tool, score };
    })
    .filter(result => result.score > 0)
    .sort((left, right) => right.score - left.score || left.tool.name.localeCompare(right.tool.name))
    .slice(0, limit);
}
```

#### 3.5 Discovery Mode 激活 {#_3-5-discovery-mode-激活}

位置：`packages/coding-agent/src/tools/search-tool-bm25.ts`（行 194-201）

通过 `tools.discoveryMode` 控制：

```typescript
static createIf(session: ToolSession): SearchToolBm25Tool | null {
  const toolsDiscoveryMode = session.settings.get("tools.discoveryMode");
  const active =
    (toolsDiscoveryMode !== undefined && toolsDiscoveryMode !== "off") ||
    session.settings.get("mcp.discoveryMode") === true;
  if (!active) return null;
  return supportsToolDiscoveryExecution(session) ? new SearchToolBm25Tool(session) : null;
}
```

索引在 `ToolSession` 上懒构建并缓存：

```typescript
function getDiscoverableToolSearchIndexForExecution(session: ToolSession): DiscoverableToolSearchIndex {
  try {
    const cached = session.getDiscoverableToolSearchIndex?.();
    if (cached) return cached;
  } catch {}
  return buildDiscoverableToolSearchIndex(getDiscoverableToolsForDescription(session));
}
```

---

### 4. oh-my-pi LSP/DAP Integration {#_4-oh-my-pi-lsp-dap-integration}

#### 4.1 LSP Client 架构 {#_4-1-lsp-client-架构}

位置：`packages/coding-agent/src/lsp/client.ts`

通过自定义帧协议在 stdio 上传输 JSON-RPC 消息：

```typescript
// 消息解析（行 179-216）
function parseMessage(buffer: Buffer): { message: LspJsonRpcResponse | LspJsonRpcNotification; remaining: Buffer } | null {
  const headerEndIndex = findHeaderEnd(buffer);  // 查找 \r\n\r\n
  const headerText = new TextDecoder().decode(buffer.slice(0, headerEndIndex));
  const contentLengthMatch = headerText.match(/Content-Length: (\d+)/i);
  const contentLength = Number.parseInt(contentLengthMatch[1], 10);
  // ... 在 header 后读取恰好 contentLength 字节
}

// 消息写入（行 218-225）
async function writeMessage(sink: Bun.FileSink, message: LspJsonRpcRequest | ...): Promise<void> {
  const content = JSON.stringify(message);
  sink.write(`Content-Length: ${Buffer.byteLength(content, "utf-8")}\r\n\r\n${content}`);
  await sink.flush();
}
```

#### 4.2 LSP Server Lifecycle {#_4-2-lsp-server-lifecycle}

位置：`packages/coding-agent/src/lsp/client.ts`（行 424-558）

```typescript
export async function getOrCreateClient(config: ServerConfig, cwd: string, initTimeoutMs?: number): Promise<LspClient> {
  const key = `${config.command}:${cwd}`;

  // 如支持则用 lspmux 包装器
  const { command, args, env } = isLspmuxSupported(baseCommand)
    ? await getLspmuxCommand(baseCommand, baseArgs)
    : { command: baseCommand, args: baseArgs };

  const proc = ptree.spawn([command, ...args], { cwd, stdin: "pipe", env });

  // Initialize handshake
  const initResult = await sendRequest(client, "initialize", {
    processId: process.pid,
    rootUri: fileToUri(cwd),
    rootPath: cwd,
    capabilities: CLIENT_CAPABILITIES,
    initializationOptions: config.initOptions ?? {},
    workspaceFolders: [{ uri: fileToUri(cwd), name: cwd.split("/").pop() ?? "workspace" }],
  });

  await sendNotification(client, "initialized", {});
  return client;
}
```

#### 4.3 Client Capabilities {#_4-3-client-capabilities}

位置：`packages/coding-agent/src/lsp/client.ts`（行 67-169）

```typescript
const CLIENT_CAPABILITIES = {
  textDocument: {
    synchronization: { didSave: true, dynamicRegistration: false },
    hover: { contentFormat: ["markdown", "plaintext"] },
    definition: { dynamicRegistration: false, linkSupport: true },
    typeDefinition: { dynamicRegistration: false, linkSupport: true },
    implementation: { dynamicRegistration: false, linkSupport: true },
    references: { dynamicRegistration: false },
    documentSymbol: { hierarchicalDocumentSymbolSupport: true, symbolKind: {...} },
    rename: { prepareSupport: true },
    codeAction: { resolveSupport: { properties: ["edit"] } },
    formatting: { dynamicRegistration: false },
    rangeFormatting: { dynamicRegistration: false },
    publishDiagnostics: { relatedInformation: true, versionSupport: true, tagSupport: { valueSet: [1, 2] } },
  },
  window: { workDoneProgress: true },
  workspace: {
    applyEdit: true,
    workspaceEdit: { documentChanges: true, failureHandling: "textOnlyTransactional" },
    configuration: true,
    fileOperations: { willRename: true, didRename: true },
  },
  experimental: { snippetTextEdit: true },
};
```

#### 4.4 Diagnostics 处理 {#_4-4-diagnostics-处理}

位置：`packages/coding-agent/src/lsp/index.ts`（行 432-485）

轮询诊断直到版本更新：

```typescript
async function waitForDiagnostics(
  client: LspClient,
  uri: string,
  options: WaitForDiagnosticsOptions = {},
): Promise<Diagnostic[]> {
  const { timeoutMs = 3000, signal, minVersion, expectedDocumentVersion, allowUnversioned = true } = options;
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    throwIfAborted(signal);
    const versionOk = minVersion === undefined || client.diagnosticsVersion > minVersion;
    const diagnostics = getAcceptedDiagnostics(client.diagnostics.get(uri), expectedDocumentVersion, allowUnversioned);
    if (diagnostics !== undefined && versionOk) return diagnostics;
    await Bun.sleep(100);
  }
  // ...
}
```

#### 4.5 LSP Tool Actions {#_4-5-lsp-tool-actions}

位置：`packages/coding-agent/src/lsp/index.ts`（行 1991-2292）

`LspTool` 处理以下 action：

| Action | 说明 |
|--------|------|
| `definition` | 转到定义 |
| `type_definition` | 转到类型定义 |
| `implementation` | 转到实现 |
| `references` | 查找引用（含项目感知服务器重试逻辑）|
| `hover` | 悬停信息 |
| `code_actions` | LSP 代码动作（含 apply 支持）|
| `symbols` | 文档和工作区符号 |
| `rename` | 符号重命名 |
| `rename_file` | 通过 `workspace/willRenameFiles` 重命名文件 |
| `diagnostics` | 获取诊断（逐文件或 `*` 工作区）|
| `status` | 服务器状态 |
| `capabilities` | 服务器能力 |
| `request` | 原始 LSP 方法调用 |
| `reload` | 服务器重载 |

#### 4.6 DAP Client 架构 {#_4-6-dap-client-架构}

位置：`packages/coding-agent/src/dap/client.ts`

DAP 使用相同的 JSON-RPC 帧协议，但支持 stdio 和 socket 两种传输方式：

```typescript
export class DapClient {
  static async spawn({ adapter, cwd }: DapSpawnOptions): Promise<DapClient> {
    if (adapter.connectMode === "socket") {
      return DapClient.#spawnSocket({ adapter, cwd });
    }
    const proc = ptree.spawn([adapter.resolvedCommand, ...adapter.args], {
      cwd, stdin: "pipe", env, detached: true,  // detached = setsid 无控制 TTY
    });
    // ...
  }
}

**Socket 模式**支持（如 `dlv`）：Linux 上用 Unix domain socket `--listen=unix:<path>`，macOS 上用 TCP listener `--client-addr=127.0.0.1:<port>`

#### 4.7 DAP Session 管理

位置：`packages/coding-agent/src/dap/session.ts`

Session 追踪断点、线程、栈帧和输出：

```typescript
interface DapSession {
  id: string;
  adapter: DapResolvedAdapter;
  cwd: string;
  client: DapClient;
  status: DapSessionStatus;  // "launching" | "configuring" | "stopped" | "running" | "terminated"
  breakpoints: Map<string, DapBreakpointRecord[]>;
  threads: DapThread[];
  lastStackFrames: DapStackFrame[];
  output: string;
  stop: DapStopLocation;
}
```

---
