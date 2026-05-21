# Persistent Graph v2 — Architecture Design Document

> 作者: Sphinx | 日期: 2026-05-21 | 版本: 1.0

---

## 1. 项目目标

为 Obsidian 提供**可命名的 Graph View 预设**系统，替换当前只能保存单项配置的限制。
预设数据存入 `data.json`，可随 git 跨端同步。

### 1.1 核心需求

| ID | 需求 | 优先级 |
|----|------|--------|
| R1 | 保存当前 Graph View 完整状态为命名预设（filter + colorGroups + positions） | P0 |
| R2 | 预设列表 UI，支持单选切换 | P0 |
| R3 | 启动时自动恢复上次激活的预设 | P0 |
| R4 | 预设数据存入 `data.json`（可 git 追踪） | P0 |
| R5 | 删除/重命名预设 | P1 |
| R6 | 从 `graph.json` 导入预设 | P1 |
| R7 | 预设导出为独立 JSON 文件 | P2 |

---

## 2. Fork vs Rebuild 评估

### 2.1 现有代码分析

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码量 | 370 行 | 极小，一天可通读 |
| 结构 | ⭐⭐ | 单文件 `main.ts`，逻辑与 UI 混杂 |
| API 兼容性 | ⭐⭐ | 依赖 `obsidian@0.12.17`，基于旧版 API |
| 测试 | ⭐ | 无测试 |
| 文档 | ⭐ | 仅 README，无架构说明 |
| 构建 | ⭐⭐⭐ | esbuild，简洁可靠 |
| 许可证 | ⭐⭐⭐ | MIT，可自由修改 |

### 2.2 需要改动的部分

| 模块 | 现有 | 需改为 | 影响 |
|------|------|--------|------|
| 数据模型 | 单一 `nodePositions + globalOptions` | `presets[]` 数组 + `activePreset` | 核心 |
| 设置 UI | 3 个 toggle | 预设选择器 + toggle | 重写 |
| 保存命令 | `saveGraphData()` | `saveCurrentAsPreset(name)` | 重构 |
| 恢复命令 | `restoreGraphData()` | `activatePreset(name)` | 重构 |
| 自动恢复 | `onLayoutChange` 恢复位置 | 恢复位置 + 滤镜 + 颜色组 | 扩展 |
| 版本兼容 | `obsidian@0.12.17` | `obsidian@latest` | 破坏性 |

### 2.3 决策矩阵

| 因素 | Fork 修改 | 完全重写 |
|------|-----------|---------|
| 开发速度 | **快**（改动 ~60% 代码） | 慢（从零开始） |
| 代码质量 | 中（继承债务） | **高**（按现代标准） |
| 测试覆盖 | 0 → 需补 | 从头加 |
| 依赖风险 | 低（esbuild + obsidian 类型） | 低（同样依赖） |
| 社区基础 | 105 stars，已分发 | 0，需从零推广 |
| 项目结构 | 单文件 → 需拆分 | 天然多文件 |
| 学习成本 | 需理解旧逻辑 | 需全部设计 |
| **GitHub fork 关联** | **保留上游链接** | 独立仓库 |

### 2.4 结论：**Fork + 重构**

理由：
1. 代码量仅 370 行，改动可控——不是"救不活的遗留代码"
2. `dataEngine.getOptions()` / `setOptions()` 已封装好，这是最难的部分
3. 节点位置恢复逻辑（`restoreOnceNodeCountStable` 等）直接复用
4. 保留 fork 链，可向上游提 PR
5. 改动边界清晰：数据层、UI 层重写，核心 Graph 交互保留

**重构策略：**
- Phase 1：拆分 `main.ts` → `main.ts` + `preset-manager.ts` + `settings-tab.ts`
- Phase 2：升级 Obsidian API 版本依赖
- Phase 3：实现预设 CRUD
- Phase 4：改进 UI

---

## 3. 架构设计

### 3.1 分层架构

```
┌─────────────────────────────────────────────────┐
│                  Settings Tab UI                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 预设列表  │  │ 保存按钮  │  │ 设置 toggle   │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│              PresetManager (业务逻辑)             │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ save()   │  │ load()   │  │ activate()    │  │
│  │ delete() │  │ rename() │  │ validate()    │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│              Graph Interface (Obsidian API)       │
│  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ dataEngine        │  │ renderer (Worker)    │  │
│  │ .getOptions()     │  │ .nodes               │  │
│  │ .setOptions(opts) │  │ .worker.postMessage  │  │
│  └──────────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────┤
│              Plugin Core (生命周期)                │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ onload() │  │ onunload │  │ event hooks   │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────┘
```

### 3.2 文件结构

```
obsidian-persistent-graph/
├── src/
│   ├── main.ts                  # 插件入口，生命周期 (~60 行)
│   ├── preset-manager.ts        # 预设 CRUD + 激活逻辑 (~150 行)
│   ├── settings-tab.ts          # 设置面板 UI (~120 行)
│   ├── graph-interface.ts       # Graph API 封装 (~80 行)
│   └── types.ts                 # 类型定义 (~50 行)
├── manifest.json
├── package.json
├── esbuild.config.mjs
├── tsconfig.json
├── README.md
├── ARCHITECTURE.md              # 本文档
└── tests/
    └── preset-manager.test.ts
```

### 3.3 数据模型

```typescript
// src/types.ts

/** 单个 Graph 预设 — dataEngine.getOptions() 的完整快照 */
interface Preset {
  id: string;                    // UUID v4
  name: string;                  // "运动健康" / "技术" / "全图"
  options: GraphOptions;         // getOptions() 完整返回
  nodePositions: NodePosition[]; // 节点坐标快照
  createdAt: string;             // ISO 8601
  updatedAt: string;
}

/** Graph View 可持久化的配置项 */
interface GraphOptions {
  search: string;
  "collapse-filter": boolean;
  "collapse-color-groups": boolean;
  colorGroups: ColorGroup[];
  showTags: boolean;
  showAttachments: boolean;
  hideUnresolved: boolean;
  showOrphans: boolean;
  "collapse-display": boolean;
  showArrow: boolean;
  "collapse-forces": boolean;
  centerStrength: number;
  repelStrength: number;
  linkStrength: number;
  linkDistance: number;
  scale: number;
  [key: string]: any;            // 向前兼容未来新增项
}

interface ColorGroup {
  query: string;
  color: { a: number; rgb: number };
}

interface NodePosition {
  id: string;   // 文件路径
  x: number;
  y: number;
}

/** 插件持久化存储结构 → data.json */
interface PersistentGraphSettings {
  presets: Preset[];
  activePresetId: string | null;
  restoreOnStartup: boolean;
  version: number;               // 数据迁移用
}
```

### 3.4 核心模块接口

```typescript
// src/preset-manager.ts

class PresetManager {
  constructor(plugin: Plugin);

  // === CRUD ===
  saveCurrentAsPreset(name: string): Promise<Preset>;
  /** 从当前打开的 Graph View 抓取完整状态并保存 */

  deletePreset(id: string): Promise<void>;
  renamePreset(id: string, newName: string): Promise<void>;
  listPresets(): Preset[];

  // === 激活 ===
  activatePreset(id: string): Promise<void>;
  /** 1. 调用 dataEngine.setOptions(preset.options)
   *   2. 调用 renderer.worker.postMessage 恢复节点位置
   *   3. 更新 activePresetId */

  restoreLastActive(): Promise<void>;
  /** 启动时调用：如果有 restoreOnStartup && activePresetId，自动激活 */

  // === 导入导出 ===
  importFromGraphJson(): Promise<Preset | null>;
  /** 读取 .obsidian/graph.json，转换为预设 */

  exportPresetToFile(id: string, path: string): Promise<void>;
}

// src/graph-interface.ts

class GraphInterface {
  /** 获取当前活跃的 Graph Leaf */
  static findGraphLeaf(app: App): CustomLeaf | null;

  /** 抓取当前 Graph View 完整状态 */
  static captureState(leaf: CustomLeaf): {
    options: GraphOptions;
    nodePositions: NodePosition[];
  };

  /** 应用预设到 Graph View */
  static applyPreset(leaf: CustomLeaf, preset: Preset): void;

  /** 等待 Graph 渲染完成（节点数稳定） */
  static waitForStable(leaf: CustomLeaf, timeout?: number): Promise<void>;
}
```

### 3.5 事件流

```
用户操作                        插件内部                          Obsidian
────────                      ────────                          ────────

打开 Graph View ──────→ layout-change event ──→ restoreLastActive()
                                                     │
                                              GraphInterface.findGraphLeaf()
                                                     │
                                              dataEngine.setOptions(preset.options)
                                              worker.postMessage(forceNode...)
                                                     │
                                                     └──→ Graph 渲染完成

点"保存当前为预设" ──→ PresetManager.saveCurrentAsPreset("运动健康")
                              │
                     GraphInterface.captureState(leaf)
                              │
                     presets.push(new Preset(...))
                              │
                     saveData(settings)  →  data.json 落盘

选预设切换 ──────────→ PresetManager.activatePreset(id)
                              │
                     从 presets 数组取 Preset
                              │
                     GraphInterface.applyPreset(leaf, preset)
                              │
                     saveData(settings)
```

### 3.6 数据迁移

```typescript
// 从旧版 Persistent Graph (v0.1.5) 迁移到 v2
async function migrateFromV1(): Promise<void> {
  const old = await loadData();
  if (old.nodePositions && !old.presets) {
    settings.presets = [{
      id: "migrated-v1",
      name: "旧版数据 (已迁移)",
      options: old.globalOptions || {},
      nodePositions: old.nodePositions,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }];
    settings.version = 2;
  }
}
```

---

## 4. 依赖与环境

| 项 | 要求 | 说明 |
|----|------|------|
| Node.js | ≥18 LTS | 构建用 |
| TypeScript | ^5.4 | 严格模式 |
| esbuild | ^0.19 | 打包 |
| obsidian (类型) | ^1.7 | 最新稳定 API |
| 目标平台 | Obsidian ≥1.5.0 | Desktop + Mobile |
| 运行环境 | 浏览器（Chromium） | Obsidian 内嵌 |

---

## 5. 测试策略

| 层级 | 工具 | 覆盖 |
|------|------|------|
| 单元测试 | vitest + @testing-library/dom | PresetManager 全部方法 |
| 集成测试 | 手动 Obsidian 沙箱 vault | 预设保存 → 切换 → 自动恢复 |
| E2E | 手动 | 跨端同步（git pull → data.json） |

---

## 6. 发布计划

| 阶段 | 内容 | 交付物 |
|------|------|--------|
| M1 | Fork + 拆分文件结构 + 升级依赖 | 可编译 |
| M2 | 预设 CRUD + Settings UI | 本地可调试 |
| M3 | 自动恢复 + 数据迁移 | beta release |
| M4 | 测试 + 文档 | v2.0.0 |

---

## 7. 风险

| 风险 | 概率 | 缓解 |
|------|------|------|
| Obsidian 内部 API 变更（dataEngine 非公开） | 中 | 封装 GraphInterface，只改一处 |
| 大量节点时恢复性能 | 低 | 已有 `restoreOnceNodeCountStable`，限制 20 轮次 |
| Mobile 兼容性 | 低 | 代码不涉及桌面特有 API，`manifest.json: "isDesktopOnly": false` |
