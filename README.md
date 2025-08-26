# Sphinx's Notes

这是一个基于 VitePress 构建的技术学习笔记网站，记录了我学习过程中的各种笔记和总结。

## 项目结构

```
vitepress/
├── .vitepress/
│   └── config.mjs          # VitePress 配置文件
├── notes/                  # 笔记内容目录
│   ├── ccpp/              # C/C++ 学习笔记
│   │   ├── c/             # C 语言相关
│   │   ├── cpp/           # C++ 相关
│   │   └── index.md       # C/C++ 笔记索引
│   ├── network/           # 网络技术笔记
│   │   ├── tcpip/         # TCP/IP 协议
│   │   ├── linux_netfilter/ # Linux Netfilter
│   │   └── index.md       # 网络笔记索引
│   ├── os/                # 操作系统笔记
│   │   └── index.md       # 操作系统笔记索引
│   ├── sys/               # 系统编程笔记
│   │   ├── design_pattern/ # 设计模式
│   │   ├── fundamentals/  # 基础知识
│   │   ├── ipc/           # 进程间通信
│   │   └── index.md       # 系统编程笔记索引
│   ├── midware/           # 中间件笔记
│   │   ├── someip/        # SOME/IP 相关
│   │   └── index.md       # 中间件笔记索引
│   └── tools/             # 工具使用笔记
│       └── index.md       # 工具笔记索引
├── index.md               # 网站首页
└── README.md              # 项目说明
```

## 技术栈

- **VitePress** - 静态站点生成器
- **Vue.js** - 前端框架
- **Markdown** - 内容编写格式

## 开发指南

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

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

## 内容组织

### 笔记分类

1. **C/C++ 编程** - C 和 C++ 语言学习笔记
2. **网络技术** - 网络协议和网络编程笔记
3. **操作系统** - 操作系统原理和内核开发笔记
4. **系统编程** - 底层系统编程和 IPC 笔记
5. **中间件** - 汽车网络协议和中间件技术笔记
6. **工具使用** - 各种开发工具的使用笔记

### 添加新笔记

1. 在相应的目录下创建 `.md` 文件
2. 在对应的 `index.md` 中添加链接
3. 在 `.vitepress/config.mjs` 中更新侧边栏配置

## 部署

本项目可以部署到任何支持静态网站的平台上，如：

- GitHub Pages
- Netlify
- Vercel
- 阿里云 OSS
- 腾讯云 COS

## 许可证

MIT License
