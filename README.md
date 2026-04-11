# Sphinx's Notes

技术学习笔记和总结，涵盖 C/C++、网络、操作系统、系统编程等多个技术领域。

## 📖 在线访问

- **GitHub Pages**: [https://sphinxes0o0.github.io/notes/](https://sphinxes0o0.github.io/notes/)

## 🚀 本地开发

### 环境要求

- Node.js 18+
- npm

### 安装依赖

```bash
npm install
```

### 本地开发服务器

```bash
npm run docs:dev
```

### 构建生产版本

```bash
npm run docs:build
```

### 预览生产版本

```bash
npm run docs:preview
```

## 🔄 自动部署

本项目配置了 GitHub Actions 自动部署到 GitHub Pages：

1. **触发条件**: 当代码推送到 `main` 分支时自动触发
2. **构建过程**: 
   - 安装 Node.js 18
   - 安装项目依赖
   - 构建 VitePress 文档
   - 部署到 GitHub Pages

### Workflow 文件位置

- `.github/workflows/deploy.yml` - 自动部署配置


## 📁 项目结构

```
notes/
├── .vitepress/          # VitePress 配置
├── courses/             # 课程笔记
├── notes/               # 技术笔记
│   ├── ccpp/           # C/C++ 相关
│   ├── network/        # 网络技术
│   ├── os/             # 操作系统
│   ├── sys/            # 系统编程
│   ├── security/        # 安全工具
│   ├── midware/        # 中间件
│   └── tools/          # 工具使用
├── resources/           # 资源文件
└── index.md            # 首页
```

## 📝 内容分类

- **C/C++ 编程**: 深入 C 和 C++ 语言学习
- **网络技术**: TCP/IP 协议栈、Linux Netfilter 等
- **操作系统**: Linux 内核开发、操作系统原理
- **系统编程**: 底层系统编程、进程间通信等
- **安全工具**: 网络扫描、安全监控、入侵检测等
- **中间件**: 汽车网络协议、SOME/IP、DoIP 等
- **工具使用**: 各种开发工具的使用技巧
