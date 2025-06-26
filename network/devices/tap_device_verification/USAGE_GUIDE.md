# TAP设备测试使用指南

## 重要说明

**⚠️ 直接运行测试程序会失败！**

如果您直接运行 `./test_tap` 或 `sudo ./test_tap`，会看到类似这样的错误：
```
打开TAP设备失败: No such file or directory
获取接口标志失败: No such device
```

**原因**：TAP设备需要先加载内核模块才能创建设备文件。

## 正确的使用方法

### 方法1：使用验证脚本（推荐）

```bash
# 完整测试流程
sudo ./verification_script.sh --full

# 基本功能测试
sudo ./verification_script.sh --basic-test

# 压力测试
sudo ./verification_script.sh --stress-test

# 仅编译测试（普通用户可执行）
./verification_script.sh --compile-only

# 清理编译产物（普通用户可执行）
./verification_script.sh --clean-build
```

### 方法2：手动步骤

如果您想手动控制每个步骤：

```bash
# 1. 编译（普通用户可执行）
make clean && make all
make -f test_makefile all

# 2. 加载内核模块（需要sudo）
sudo insmod tap_device.ko

# 3. 验证设备创建
ls -l /dev/tap0
ip link show tap0

# 4. 运行测试程序（需要sudo）
sudo ./test_tap -a

# 5. 卸载模块（需要sudo）
sudo rmmod tap_device
```

### 方法3：使用Makefile快捷命令

```bash
# 完整测试流程
sudo make test

# 验证编译
make verify

# 查看模块信息
sudo make info

# 查看内核日志
sudo make dmesg

# 清理环境
make clean
```

## 测试程序选项

```bash
sudo ./test_tap [选项]

选项:
  -b          基本读写测试
  -i          网络接口测试
  -c <数量>   连续数据包测试
  -p          性能测试
  -a          运行所有测试
  -h          显示帮助
```

## 常见问题

### Q: 为什么需要sudo权限？
A: 因为需要：
- 加载/卸载内核模块
- 访问字符设备文件 (`/dev/tap0`)
- 操作网络接口

### Q: 编译需要sudo权限吗？
A: 不需要！编译可以用普通用户执行：
```bash
./verification_script.sh --compile-only
```

### Q: 如何检查模块是否已加载？
A: 使用以下命令：
```bash
lsmod | grep tap_device
ls -l /dev/tap0
ip link show tap0
```

### Q: 测试完成后如何清理？
A: 有两种清理方式：
```bash
# 完整清理（模块 + 编译产物）
sudo ./verification_script.sh --cleanup

# 仅清理编译产物（保留模块）
./verification_script.sh --clean-build
```

### Q: 为什么默认保留编译产物？
A: 
- 加快后续编译速度（从几秒到不到1秒）
- 避免重复下载内核头文件
- 方便连续开发测试
- 编译产物不会影响系统稳定性

## 文件说明

- `tap_device.c` - TAP设备内核模块源代码
- `test_tap.c` - 用户空间测试程序
- `verification_script.sh` - 自动化验证脚本
- `Makefile` - 内核模块编译脚本
- `test_makefile` - 测试程序编译脚本 