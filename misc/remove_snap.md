# Ubuntu 22.04 移除 snap

## 删除snap 软件

查看已经安装的软件
```bash
sudo snap list
```

### 停止snapd 服务
```bash
sudo systemctl disable snapd.service
sudo systemctl disable snapd.socket
sudo systemctl disable snapd.seeded.service
```

### 依次移除snap 安装的软件
运行 `sudo snap remove --purge snap-store` 等命令依次删除前面列表中的各个软件 
需要注意的是,在上述列表中base的表示是其他软件的依赖项，需要放在最后面删除。
比如上图中的 `bare`, `core20`, `core22`等等

使用脚本快速删除：
```bash
for p in $(snap list | awk '{print $1}'); do
  sudo snap remove $p
done
```

### 删除snapd
最后运行 `sudo snap remove --purge snapd` 


### 完全清除 snapd
使用apt卸载snapd服务
`sudo apt autoremove --purge snapd` 

删除缓存目录（如果有）

```bash
rm -rf ~/snap
sudo rm -rf /snap
sudo rm -rf /var/snap
sudo rm -rf /var/lib/snapd
```

## 防止apt update自动安装snap

以上命令只是移除了 Snap 软件包，默认情况下由于没有关闭 apt 触发器，
`sudo apt update`命令会再一次将 Snap 安装回来。

要通过配置文件来关闭它，在 `/etc/apt/preferences.d/` 目录下创建一个 apt 设置文件 `nosnap.pref`

```bash
# 运行命令
sudo gedit /etc/apt/preferences.d/nosnap.pref
```

打开编辑器，输入以下内容并保存文件

```bash
Package: snapd
Pin: release a=*
Pin-Priority: -10
```
保存后运行 `sudo apt update` 
