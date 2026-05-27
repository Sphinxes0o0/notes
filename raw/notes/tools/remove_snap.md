# Ubuntu 22.04 移除 snap

## 什么是 snap

Snap 是 Canonical 开发的一种软件打包和分发格式，旨在解决传统 Linux 包管理的一些问题。与传统的 deb/rpm 包相比，snap 具有以下特点：

- **自包含**：snap 包包含了应用程序及其所有依赖，减少"依赖地狱"
- **事务更新**：支持原子更新，更新失败可以自动回滚
- **沙箱隔离**：snap 应用运行在隔离环境中，提高安全性
- **并行安装**：同一应用的多个版本可以共存

但是，snap 在实际使用中也有一些问题：
- **性能开销**：沙箱机制带来一定的性能损失
- **磁盘空间**：snap 包体积通常比 deb 包大
- **启动速度**：首次启动较慢
- **权限配置复杂**：需要配置 interface 连接才能访问系统资源

## 为什么移除 snap

很多用户选择移除 snap 的原因包括：

1. **性能考虑**：snap 应用的启动和运行速度通常比传统 deb 包慢
2. **磁盘空间**：snap 占用的磁盘空间通常更大
3. **资源占用**：snapd 服务会占用一定的系统资源
4. **使用习惯**：很多用户习惯使用 apt 和传统的包管理方式
5. **企业环境**：某些企业环境不需要 snap 的特性

## 删除 snap 软件

### 查看已安装的软件

在开始移除之前，首先查看系统中已安装的 snap 软件：

```bash
sudo snap list
```

典型输出可能如下：

```
Name               Version    Rev   Tracking       Publisher   Notes
bare               1.0        20    latest/stable  canonical   base
core20             20230126   1622  latest/stable  canonical   base
core22             20230126   634  latest/stable  canonical   base
gtk-common-themes  1535       1515  latest/stable  canonical   -
snap-store         41.3-71    736  latest/stable  canonical   -
snapd              2.58       15177 latest/stable  canonical   -
```

可以看到，主要包括：
- **base**：其他 snap 的基础依赖（如 bare, core20, core22）
- **gtk-common-themes**：GTK 主题
- **snap-store**：Ubuntu 软件商店
- **snapd**：snapd 服务本身

### 停止 snapd 服务

在移除软件之前，需要先停止 snapd 相关的服务：

```bash
sudo systemctl disable snapd.service
sudo systemctl disable snapd.socket
sudo systemctl disable snapd.seeded.service
```

这三个服务的作用：
- **snapd.service**：snapd 主服务
- **snapd.socket**：snapd 的套接字激活服务
- **snapd.seeded.service**：首次引导时初始化 snap 的服务

停止这些服务可以防止它们在系统启动时自动运行。

### 依次移除 snap 安装的软件

运行以下命令依次删除各个 snap 包。需要注意的是，base 类型的 snap（如 bare, core20, core22）是其他软件的依赖项，需要放在最后删除：

```bash
sudo snap remove --purge snap-store
sudo snap remove --purge gtk-common-themes
sudo snap remove --purge bare
sudo snap remove --purge core20
sudo snap remove --purge core22
```

使用脚本快速删除（不推荐跳过 base 的依赖检查）：

```bash
for p in $(snap list | awk '{print $1}'); do
  sudo snap remove $p
done
```

或者强制删除所有（包括 base，但可能影响其他依赖这些 base 的 snap）：

```bash
for p in $(snap list | awk '{print $1}' | grep -v "^Name$"); do
  sudo snap remove --purge $p 2>/dev/null || true
done
```

### 删除 snapd

最后删除 snapd 本身：

```bash
sudo snap remove --purge snapd
```

或者如果上述命令失败，可以尝试：

```bash
sudo snap remove snapd
```

## 完全清除 snapd

### 使用 apt 卸载 snapd

即使删除了所有 snap 包，snapd 的 apt 包仍然存在。使用以下命令完全卸载：

```bash
sudo apt autoremove --purge snapd
```

`autoremove --purge` 会删除 snapd 以及所有不再需要的依赖项。

### 清理残留文件和目录

删除 snap 相关的缓存和配置目录：

```bash
# 删除用户 snap 缓存
rm -rf ~/snap

# 删除系统 snap 目录
sudo rm -rf /snap

# 删除系统 snap 运行时目录
sudo rm -rf /var/snap

# 删除 snapd 数据目录
sudo rm -rf /var/lib/snapd

# 删除 snapd 配置文件（可选）
sudo rm -rf /etc/snapd

# 删除 snapd 锁文件
sudo rm -rf /run/snapd
```

完整的清理脚本：

```bash
#!/bin/bash
# snap-cleanup.sh - 完全清理 snap

echo "Stopping snapd services..."
sudo systemctl stop snapd.service snapd.socket snapd.seeded.service 2>/dev/null

echo "Disabling snapd services..."
sudo systemctl disable snapd.service snapd.socket snapd.seeded.service 2>/dev/null

echo "Removing snap packages..."
for p in $(snap list 2>/dev/null | awk 'NR>1 {print $1}'); do
    sudo snap remove --purge "$p" 2>/dev/null
done

echo "Removing snapd..."
sudo apt autoremove --purge -y snapd

echo "Cleaning up directories..."
rm -rf ~/snap 2>/dev/null
sudo rm -rf /snap /var/snap /var/lib/snapd /etc/snapd /run/snapd 2>/dev/null

echo "Done!"
```

## 防止 apt update 自动安装 snap

上述步骤只是移除了 snap 软件包。默认情况下，Ubuntu 22.04 会将 snapd 作为某些软件包的依赖自动安装。例如，安装 `gnome-software` 或 `ubuntu-desktop` 时可能会触发 snapd 的安装。

### 方法一：使用 apt Pinning

通过配置文件来阻止 apt 安装 snapd。在 `/etc/apt/preferences.d/` 目录下创建 apt 配置文件：

```bash
sudo nano /etc/apt/preferences.d/nosnap.pref
```

输入以下内容并保存：

```bash
Package: snapd
Pin: release a=*
Pin-Priority: -10
```

这个配置的含义：
- **Package**：指定要 pin 的包名
- **Pin: release a=***：匹配所有发布版本（a 表示 Archive）
- **Pin-Priority: -10**：负优先级，使得 apt 不会主动安装这个包

保存后运行：

```bash
sudo apt update
```

验证配置生效后，尝试安装 snapd 应该会被阻止：

```bash
sudo apt install snapd
```

应该会看到类似输出表明安装被阻止：

```
Package snapd is pinned by the user.
```

### 方法二：使用 apt-mark

将 snapd 标记为 hold，防止其被安装或升级：

```bash
sudo apt-mark hold snapd
```

查看 hold 状态的包：

```bash
apt-mark showhold
```

取消 hold（如果将来需要重新安装 snap）：

```bash
sudo apt-mark unhold snapd
```

### 方法三：完全移除 snap 相关的元数据包

Ubuntu 22.04 中某些 gnome 软件包依赖 snap。完全避免 snap 的另一种方法是安装替代软件：

```bash
# 移除 gnome-software（它会推荐安装 snapd）
sudo apt remove --autoremove gnome-software

# 安装 synaptic 作为替代包管理器
sudo apt install synaptic
```

## 验证移除完成

完成所有步骤后，验证 snap 已被完全移除：

```bash
# 检查 snap 命令是否还存在
which snap

# 检查 snapd 服务状态
systemctl status snapd

# 检查 snapd 包状态
dpkg -l | grep snapd

# 检查 snap 目录
ls -la /snap
ls -la ~/snap
```

如果所有命令都表明 snap 不存在，说明移除成功。

## 替代包管理方案

移除 snap 后，可以考虑以下替代方案：

| 替代方案 | 说明 |
|---------|------|
| **apt** | Ubuntu 默认的包管理器 |
| **synaptic** | 图形化包管理器，功能强大 |
| **flatpak** | 另一种沙箱化包格式，与 snap 类似但社区更活跃 |
| **appimage** | 无需安装的便携式应用格式 |
| **deb** | 直接下载 .deb 包安装 |

如果需要安装 Flatpak：

```bash
sudo apt install flatpak
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

## 常见问题

### Q: 为什么删除 snap 后 /snap 目录还在？

这通常是因为目录中有系统或其他工具创建的内容。使用 `sudo rm -rf /snap` 可以删除。

### Q: 如何重新安装 snap？

如果将来需要重新安装 snap，可以：

```bash
# 移除 apt pinning
sudo rm /etc/apt/preferences.d/nosnap.pref

# 移除 apt hold
sudo apt-mark unhold snapd

# 重新安装
sudo apt update
sudo apt install snapd

# 启用服务
sudo systemctl enable --now snapd.socket
sudo systemctl enable --now snapd.apparmor
```

### Q: Ubuntu Core 是否可以使用本指南？

Ubuntu Core 是专为 IoT 和嵌入式设备设计的版本，它完全基于 snap。本指南不适用于 Ubuntu Core。

### Q: 如何只禁用 snap 而不完全删除？

如果只是想禁用 snap 而不是完全删除：

```bash
# 停止服务
sudo systemctl stop snapd.service snapd.socket

# 禁用服务
sudo systemctl disable snapd.service snapd.socket

# 屏蔽服务（防止其他服务启动它）
sudo systemctl mask snapd.service
```

这样 snap 不会自动运行，但仍然可以手动启动。
