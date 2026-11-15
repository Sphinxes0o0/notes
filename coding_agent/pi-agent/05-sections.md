---
title: "4. Subagent Task Fan-out 机制"
---

# 4. Subagent Task Fan-out 机制 {#chapter}

[返回总目录](../pi-agent)

### 4. Subagent Task Fan-out 机制 {#_4-subagent-task-fan-out-机制}

oh-my-pi 支持将任务**并行分发给多个独立子代理**，每个子代理在隔离的 Git Worktree 中运行，结果通过 Schema 验证合并。

#### 核心 API {#核心-api}

```typescript
// src/coordination/fanout.ts

interface FanoutTask<T> {
  id: string;
  description: string;
  prompt: string;
  tools?: string[];           // 允许的工具白名单
  worktree?: string;          // Git worktree 路径，默认自动创建
  model?: string;             // 可选的模型覆盖
  timeout?: number;          // 超时 ms，默认 5 分钟
  schema?: z.ZodType<T>;      // 返回值 Schema
}

interface FanoutResult<T> {
  taskId: string;
  success: boolean;
  result?: T;
  error?: string;
  duration: number;
  tokensUsed?: number;
}

interface FanoutOptions {
  parallelism?: number;      // 最大并发数，默认 4
  stopOnError?: boolean;     // 一个失败则全部取消，默认 false
  merge?: 'all' | 'successful' | 'first';
}

// 主调度器
class TaskFanout {
  constructor(
    private agent: Agent,           // 主代理引用
    private executor: Executor,      // 子代理执行器
    private validator: Validator,    // Schema 验证器
  ) {}

  async fanout<T>(
    tasks: FanoutTask<T>[],
    options: FanoutOptions = {}
  ): Promise<FanoutResult<T>[]> {
    const {
      parallelism = 4,
      stopOnError = false,
      merge = 'successful',
    } = options;

    // 1. 准备 worktrees
    const preparedTasks = await this.prepareTasks(tasks);

    // 2. 创建任务队列 (信号量控制并发)
    const semaphore = new Semaphore(parallelism);
    const results: FanoutResult<T>[] = [];
    const errors: Error[] = [];

    // 3. 并行执行
    const promises = preparedTasks.map(async (task) => {
      await semaphore.acquire();
      try {
        return await this.executeTask<T>(task);
      } finally {
        semaphore.release();
      }
    });

    // 4. 收集结果
    const settled = await Promise.allSettled(promises);
    
    for (let i = 0; i < settled.length; i++) {
      const outcome = settled[i];
      if (outcome.status === 'fulfilled') {
        results.push(outcome.value);
      } else {
        if (stopOnError) {
          await this.cancelRemaining(preparedTasks.slice(i));
          throw new Error(`Task ${i} failed: ${outcome.reason}`);
        }
        results.push({
          taskId: tasks[i].id,
          success: false,
          error: outcome.reason?.message ?? 'Unknown error',
          duration: 0,
        });
      }
    }

    // 5. 合并结果
    return this.mergeResults(results, merge);
  }

  private async executeTask<T>(task: PreparedTask): Promise<FanoutResult<T>> {
    const start = Date.now();
    const subagent = this.executor.createSubagent({
      worktree: task.worktree,
      tools: task.tools,
      model: task.model,
      systemPrompt: task.systemPrompt,
    });

    const stream = await subagent.run(task.prompt);
    let fullResponse = '';

    for await (const chunk of stream) {
      fullResponse += chunk;
    }

    // Schema 验证
    let parsed: T | undefined;
    let error: string | undefined;

    if (task.schema) {
      try {
        parsed = this.validator.parse(fullResponse, task.schema);
      } catch (e) {
        error = `Schema validation failed: ${e.message}`;
      }
    } else {
      parsed = fullResponse as unknown as T;
    }

    return {
      taskId: task.id,
      success: !error,
      result: parsed,
      error,
      duration: Date.now() - start,
      tokensUsed: subagent.lastUsage?.total_tokens,
    };
  }

  private async prepareTasks<T>(tasks: FanoutTask<T>[]): Promise<PreparedTask[]> {
    return Promise.all(tasks.map(async (task) => {
      // 为每个任务创建独立的 Git worktree
      const worktree = task.worktree ?? await this.createWorktree(task.id);
      return {
        ...task,
        worktree,
        systemPrompt: this.buildSystemPrompt(task),
      };
    }));
  }

  private async createWorktree(id: string): Promise<string> {
    const branchName = `pi-fanout-${id}-${Date.now()}`;
    const worktreePath = path.join(
      process.env.PI_FANOUT_DIR ?? '/tmp/pi-fanout',
      id
    );

    // git worktree add <path> <branch>
    await this.agent.exec('git', ['worktree', 'add', worktreePath, '-b', branchName]);
    
    return worktreePath;
  }
}
```

#### Schema 验证的返回类型示例 {#schema-验证的返回类型示例}

```typescript
import { z } from 'zod';

// 定义子任务返回 Schema
const FileAnalysisSchema = z.object({
  file: z.string(),
  linesOfCode: z.number(),
  complexity: z.enum(['low', 'medium', 'high']),
  issues: z.array(z.object({
    line: z.number(),
    severity: z.enum(['error', 'warning', 'info']),
    message: z.string(),
  })),
  summary: z.string().max(200),
});

// 使用 fan-out
const results = await fanout.fanout([
  {
    id: 'analyze-auth',
    description: 'Analyze authentication module',
    prompt: 'Analyze /src/auth/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
  {
    id: 'analyze-api',
    description: 'Analyze API layer',
    prompt: 'Analyze /src/api/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
  {
    id: 'analyze-db',
    description: 'Analyze database layer',
    prompt: 'Analyze /src/db/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
], {
  parallelism: 3,
  merge: 'all',
});

// 类型安全的结果
for (const r of results) {
  if (r.success && r.result) {
    const analysis: z.infer<typeof FileAnalysisSchema> = r.result;
    console.log(`${analysis.file}: ${analysis.linesOfCode} LOC, ${analysis.issues.length} issues`);
  }
}
```

#### Worktree 隔离机制 {#worktree-隔离机制}

```rust
// src/coordination/worktree.rs

pub struct WorktreeManager {
    repo_path: PathBuf,
    worktrees: HashMap<String, WorktreeHandle>,
    base_branch: String,
}

pub struct WorktreeHandle {
    path: PathBuf,
    branch: String,
    _guard: WorktreeGuard,  // Drop 时清理
}

impl WorktreeManager {
    pub async fn create(&self, id: &str) -> Result<WorktreeHandle> {
        let branch = format!("pi-fanout-{}-{}", id, uuid::Uuid::new_v4());
        let path = self.repo_path.join(".git").join("worktrees").join(id);
        
        // git worktree add <path> -b <branch>
        self.run_git(&[
            "worktree", "add",
            path.as_os_str(),
            "-b", branch.as_str(),
        ]).await?;
        
        Ok(WorktreeHandle {
            path,
            branch,
            _guard: WorktreeGuard { id: id.to_string(), manager: self },
        })
    }
}

impl Drop for WorktreeGuard {
    fn drop(&mut self) {
        // 清理 worktree (可选：保留供后续检查)
        if let Ok(worktrees) = self.manager.list() {
            if let Some(wt) = worktrees.get(&self.id) {
                // git worktree remove <path>
                self.manager.run_git(&["worktree", "remove", wt.path.as_os_str()]).ok();
                // git branch -D <branch>
                self.manager.run_git(&["branch", "-D", &wt.branch]).ok();
            }
        }
    }
}
```

**Fan-out 典型用例:**

| 场景 | 分发数 | 说明 |
|------|--------|------|
| 并行文件搜索 | N×路径 | 每个路径一个子代理，结果合并 |
| 跨多个仓库扫描 | N×仓库 | Git worktree 隔离 |
| 大文件分段分析 | N×区块 | 行范围切分，并行解析 |
| 多语言代码审查 | N×语言 | 每个语言独立分析流 |
| PR 分支对比 | N×分支 | 每个分支独立审查后汇总 |

---

## License {#license}

MIT License

---

