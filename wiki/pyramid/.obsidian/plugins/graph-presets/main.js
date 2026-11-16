"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/main.ts
var main_exports = {};
__export(main_exports, {
  default: () => GraphPresetsPlugin
});
module.exports = __toCommonJS(main_exports);
var import_obsidian5 = require("obsidian");

// src/types.ts
var DEFAULT_SETTINGS = {
  presets: [],
  activePresetId: null,
  restoreOnStartup: true
};

// src/preset-manager.ts
var import_obsidian2 = require("obsidian");

// src/graph-interface.ts
var import_obsidian = require("obsidian");
var GraphInterface = class _GraphInterface {
  static findLeaf(app) {
    const leaves = app.workspace.getLeavesOfType("graph");
    if (leaves.length === 0) {
      new import_obsidian.Notice("No Graph View open");
      return null;
    }
    const active = app.workspace.activeLeaf;
    if (active?.view.getViewType() === "graph") {
      return active;
    }
    return leaves[0];
  }
  static captureOptions(leaf) {
    return leaf.view.dataEngine.getOptions();
  }
  static capturePositions(leaf) {
    return leaf.view.renderer.nodes.map((n) => ({
      id: n.id,
      x: n.x,
      y: n.y
    }));
  }
  static applyOptions(leaf, options) {
    leaf.view.dataEngine.setOptions(options);
  }
  static applyPositions(leaf, positions) {
    const worker = leaf.view.renderer.worker;
    positions.forEach((node) => {
      worker.postMessage({ forceNode: node });
    });
    worker.postMessage({ run: true, alpha: 0.1 });
    setTimeout(() => {
      positions.forEach((node) => {
        worker.postMessage({ forceNode: { id: node.id, x: null, y: null } });
      });
    }, 600);
  }
  static waitForStable(leaf, stableCount, iterations, maxIterations, onReady) {
    if (maxIterations > 20)
      return;
    const current = leaf.view.renderer.nodes.length;
    if (current === stableCount && iterations >= 3) {
      onReady();
    } else {
      const nextStable = current === stableCount ? stableCount : current;
      const nextIter = current === stableCount ? iterations + 1 : 0;
      setTimeout(() => {
        _GraphInterface.waitForStable(
          leaf,
          nextStable,
          nextIter,
          maxIterations + 1,
          onReady
        );
      }, 200);
    }
  }
};

// src/preset-manager.ts
var PresetManager = class {
  constructor(app, getSettings, saveSettings) {
    this.app = app;
    this.getSettings = getSettings;
    this.saveSettings = saveSettings;
  }
  list() {
    return this.getSettings().presets;
  }
  get(id) {
    return this.getSettings().presets.find((p) => p.id === id);
  }
  get activePresetId() {
    return this.getSettings().activePresetId;
  }
  async saveCurrent(name) {
    const leaf = GraphInterface.findLeaf(this.app);
    if (!leaf)
      throw new Error("No Graph View open");
    const preset = {
      id: crypto.randomUUID(),
      name,
      options: GraphInterface.captureOptions(leaf),
      nodePositions: GraphInterface.capturePositions(leaf),
      createdAt: (/* @__PURE__ */ new Date()).toISOString(),
      updatedAt: (/* @__PURE__ */ new Date()).toISOString()
    };
    const settings = this.getSettings();
    settings.presets.push(preset);
    await this.saveSettings();
    new import_obsidian2.Notice(`Preset "${name}" saved`);
    return preset;
  }
  async updateCurrent(id) {
    const leaf = GraphInterface.findLeaf(this.app);
    if (!leaf)
      throw new Error("No Graph View open");
    const preset = this.get(id);
    if (!preset)
      throw new Error("Preset not found");
    preset.options = GraphInterface.captureOptions(leaf);
    preset.nodePositions = GraphInterface.capturePositions(leaf);
    preset.updatedAt = (/* @__PURE__ */ new Date()).toISOString();
    await this.saveSettings();
    new import_obsidian2.Notice(`Preset "${preset.name}" updated`);
  }
  async activate(id) {
    const preset = this.get(id);
    if (!preset)
      throw new Error("Preset not found");
    const leaf = GraphInterface.findLeaf(this.app);
    if (!leaf)
      throw new Error("No Graph View open");
    GraphInterface.applyOptions(leaf, preset.options);
    GraphInterface.applyPositions(leaf, preset.nodePositions);
    const settings = this.getSettings();
    settings.activePresetId = id;
    await this.saveSettings();
    new import_obsidian2.Notice(`Activated: ${preset.name}`);
  }
  async restoreLastActive() {
    const settings = this.getSettings();
    if (!settings.restoreOnStartup || !settings.activePresetId)
      return;
    const leaf = GraphInterface.findLeaf(this.app);
    if (!leaf)
      return;
    const preset = this.get(settings.activePresetId);
    if (!preset)
      return;
    GraphInterface.waitForStable(leaf, leaf.view.renderer.nodes.length, 0, 0, () => {
      GraphInterface.applyOptions(leaf, preset.options);
      GraphInterface.applyPositions(leaf, preset.nodePositions);
    });
  }
  async delete(id) {
    const settings = this.getSettings();
    const idx = settings.presets.findIndex((p) => p.id === id);
    if (idx < 0)
      return;
    const name = settings.presets[idx].name;
    settings.presets.splice(idx, 1);
    if (settings.activePresetId === id) {
      settings.activePresetId = null;
    }
    await this.saveSettings();
    new import_obsidian2.Notice(`Preset "${name}" deleted`);
  }
  async rename(id, newName) {
    const preset = this.get(id);
    if (!preset)
      return;
    preset.name = newName;
    preset.updatedAt = (/* @__PURE__ */ new Date()).toISOString();
    await this.saveSettings();
  }
};

// src/settings-tab.ts
var import_obsidian3 = require("obsidian");
var GraphPresetsSettingTab = class extends import_obsidian3.PluginSettingTab {
  constructor(app, mgr, plugin) {
    super(app, plugin);
    this.mgr = mgr;
    this.plugin = plugin;
  }
  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "Graph Presets" });
    const presets = this.mgr.list();
    if (presets.length === 0) {
      containerEl.createEl("p", {
        text: "No presets yet. Open a Graph View, set up filters/colors, then click \u{1F4C1} Presets \u2192 Save.",
        cls: "setting-item-description"
      });
    } else {
      containerEl.createEl("p", {
        text: `${presets.length} preset(s). Activate them from the Graph View panel.`,
        cls: "setting-item-description"
      });
      presets.forEach((preset) => this.renderRow(containerEl, preset));
    }
  }
  renderRow(containerEl, preset) {
    const filter = preset.options.search || "(all)";
    const colors = preset.options.colorGroups?.length ?? 0;
    new import_obsidian3.Setting(containerEl).setName(preset.name).setDesc(`Filter: ${filter} \xB7 ${colors} color groups \xB7 ${preset.updatedAt.slice(0, 10)}`).addExtraButton(
      (btn) => btn.setIcon("pencil").setTooltip("Rename").onClick(() => {
        const newName = window.prompt("New name:", preset.name);
        if (newName && newName !== preset.name) {
          this.mgr.rename(preset.id, newName).then(() => this.display());
        }
      })
    ).addExtraButton(
      (btn) => btn.setIcon("trash").setTooltip("Delete").onClick(async () => {
        await this.mgr.delete(preset.id);
        this.display();
      })
    );
  }
};

// src/header-ui.ts
var import_obsidian4 = require("obsidian");
var PANEL_ID = "graph-presets-panel";
var HeaderUI = class _HeaderUI {
  static injectAll(app, presetManager) {
    _HeaderUI.app = app;
    _HeaderUI._mgr = presetManager;
    requestAnimationFrame(() => {
      const leaves = app.workspace.getLeavesOfType("graph");
      leaves.forEach((leaf) => {
        const container = leaf.view.containerEl;
        if (!container || container.querySelector(`#${PANEL_ID}`))
          return;
        _HeaderUI.injectOne(container, presetManager);
      });
    });
  }
  static injectOne(graphContainer, presetManager) {
    const panel = document.createElement("div");
    panel.id = PANEL_ID;
    panel.style.cssText = `
        position:absolute; bottom:12px; left:12px; z-index:10;
        background:var(--background-primary); border:1px solid var(--background-modifier-border);
        border-radius:8px; padding:6px 8px; font-size:12px;
        box-shadow:0 2px 8px rgba(0,0,0,0.15); min-width:200px;
      `;
    graphContainer.appendChild(panel);
    const toggleBtn = panel.createEl("button", {
      text: "\u{1F4C1} Presets",
      cls: "graph-presets-toggle"
    });
    toggleBtn.style.cssText = "font-size:12px;width:100%;cursor:pointer;";
    const body = panel.createEl("div", { cls: "graph-presets-body" });
    body.style.display = "none";
    const select = body.createEl("select", { cls: "dropdown" });
    select.style.cssText = "width:100%;margin-bottom:4px;";
    const btnRow = body.createEl("div");
    btnRow.style.cssText = "display:flex;gap:3px;";
    const primaryBtn = btnRow.createEl("button");
    primaryBtn.style.cssText = "font-size:11px;flex:1;";
    const newBtn = btnRow.createEl("button", { text: "+" });
    newBtn.style.cssText = "font-size:11px;flex:0 0 24px;";
    const delBtn = btnRow.createEl("button", { text: "\u{1F5D1}" });
    delBtn.style.cssText = "font-size:11px;flex:0 0 28px;color:var(--text-error);";
    let expanded = false;
    toggleBtn.addEventListener("click", () => {
      expanded = !expanded;
      body.style.display = expanded ? "block" : "none";
      toggleBtn.textContent = expanded ? "\u{1F4C1} Presets \u25B2" : "\u{1F4C1} Presets";
      if (expanded)
        _HeaderUI.refresh(select, primaryBtn, newBtn, presetManager);
    });
    select.addEventListener("change", async () => {
      const id = select.value;
      if (!id)
        return;
      try {
        await presetManager.activate(id);
        _HeaderUI.refresh(select, primaryBtn, newBtn, presetManager);
      } catch (e) {
        new import_obsidian4.Notice(e.message);
      }
    });
    primaryBtn.addEventListener("click", () => {
      const activeId = presetManager.activePresetId;
      if (activeId) {
        presetManager.updateCurrent(activeId).then(() => {
          _HeaderUI.refresh(select, primaryBtn, newBtn, presetManager);
        }).catch((e) => new import_obsidian4.Notice(e.message));
      } else {
        _HeaderUI.promptSave(body, select, primaryBtn, newBtn, delBtn, presetManager);
      }
    });
    newBtn.addEventListener("click", () => {
      _HeaderUI.promptSave(body, select, primaryBtn, newBtn, delBtn, presetManager);
    });
    delBtn.addEventListener("click", async () => {
      const id = select.value;
      if (!id) {
        new import_obsidian4.Notice("No preset selected");
        return;
      }
      const p = presetManager.list().find((p2) => p2.id === id);
      if (!p)
        return;
      if (confirm(`Delete "${p.name}"?`)) {
        await presetManager.delete(id);
        _HeaderUI.refresh(select, primaryBtn, newBtn, presetManager);
      }
    });
  }
  /** Show inline name input, then save as new preset */
  static promptSave(body, select, primaryBtn, newBtn, delBtn, mgr) {
    const input = body.createEl("input", {
      type: "text",
      placeholder: "preset name..."
    });
    input.style.cssText = "width:100%;margin-bottom:4px;font-size:12px;";
    primaryBtn.style.display = "none";
    newBtn.style.display = "none";
    delBtn.style.display = "none";
    const doSave = async () => {
      const name = input.value.trim();
      input.remove();
      primaryBtn.style.display = "";
      newBtn.style.display = "";
      delBtn.style.display = "";
      if (!name)
        return;
      try {
        await mgr.saveCurrent(name);
        _HeaderUI.refresh(select, primaryBtn, newBtn, mgr);
      } catch (e) {
        new import_obsidian4.Notice(e.message);
      }
    };
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter")
        doSave();
      if (e.key === "Escape") {
        input.remove();
        primaryBtn.style.display = "";
        newBtn.style.display = "";
        delBtn.style.display = "";
      }
    });
    input.focus();
  }
  static refresh(select, primaryBtn, newBtn, mgr) {
    const presets = mgr.list();
    const activeId = mgr.activePresetId;
    select.innerHTML = "";
    if (presets.length === 0) {
      const opt = select.createEl("option", { value: "", text: "No presets" });
      opt.disabled = true;
      opt.selected = true;
      primaryBtn.textContent = "Save";
      newBtn.style.display = "none";
      _HeaderUI.updateTabTitle();
      return;
    }
    const hasActive = presets.some((p) => p.id === activeId);
    primaryBtn.textContent = hasActive ? "Update" : "Save";
    newBtn.style.display = "";
    presets.forEach((p) => {
      const opt = select.createEl("option", { value: p.id, text: p.name });
      if (p.id === activeId)
        opt.selected = true;
    });
    _HeaderUI.updateTabTitle();
  }
  static updateTabTitle() {
    const leaves = _HeaderUI.app.workspace.getLeavesOfType("graph");
    leaves.forEach((leaf) => {
      const tabHeader = leaf.tabHeaderEl;
      if (!tabHeader)
        return;
      const titleEl = tabHeader.querySelector(".workspace-tab-header-inner-title");
      if (!titleEl)
        return;
      const container = leaf.view.containerEl;
      const select = container.querySelector(`#${PANEL_ID} select`);
      const selectedId = select?.value;
      let title = "Graph view";
      if (selectedId) {
        const preset = _HeaderUI._mgr?.list().find((p) => p.id === selectedId);
        if (preset)
          title = `Graph: ${preset.name}`;
      }
      titleEl.textContent = title;
    });
  }
};

// src/main.ts
var GraphPresetsPlugin = class extends import_obsidian5.Plugin {
  async onload() {
    await this.loadSettings();
    this.presetManager = new PresetManager(
      this.app,
      () => this.settings,
      async () => this.saveData(this.settings)
    );
    this.addCommand({
      id: "save-preset",
      name: "Save current graph as preset",
      callback: async () => {
        const name = `Preset ${this.settings.presets.length + 1}`;
        try {
          await this.presetManager.saveCurrent(name);
        } catch (e) {
          console.error(e.message);
        }
      }
    });
    this.addCommand({
      id: "restore-last-preset",
      name: "Restore last active preset",
      callback: () => this.presetManager.restoreLastActive()
    });
    this.addSettingTab(new GraphPresetsSettingTab(this.app, this.presetManager, this));
    this.registerEvent(
      this.app.workspace.on("layout-change", () => {
        const leaves = this.app.workspace.getLeavesOfType("graph");
        if (leaves.length > 0) {
          HeaderUI.injectAll(this.app, this.presetManager);
          HeaderUI.updateTabTitle(this.presetManager);
          if (this.settings.restoreOnStartup) {
            setTimeout(() => {
              this.presetManager.restoreLastActive();
              HeaderUI.updateTabTitle(this.presetManager);
            }, 500);
          }
        }
      })
    );
  }
  onunload() {
  }
  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }
  async saveSettings() {
    await this.saveData(this.settings);
  }
};
