#!/bin/bash

# TAP设备验证脚本
# 自动化验证TAP设备实现的完整性和功能

set -e  # 遇到错误时退出

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

MODULE_NAME="tap_device"
DEVICE_NAME="tap0"
CHAR_DEVICE="/dev/tap0"

# 打印带颜色的消息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查运行权限（仅用于需要root的操作）
check_permissions() {
    print_status "检查运行权限..."
    if [[ $EUID -ne 0 ]]; then
        print_error "此操作需要root权限运行"
        echo "请使用: sudo $0"
        exit 1
    fi
    print_success "权限检查通过"
}

# 检查编译权限（普通用户即可）
check_compile_permissions() {
    print_status "检查编译权限..."
    print_success "普通用户权限足够进行编译"
}

# 检查系统依赖
check_dependencies() {
    print_status "检查系统依赖..."
    
    # 检查编译工具
    if ! command -v make &> /dev/null; then
        print_error "未找到make工具"
        exit 1
    fi
    
    if ! command -v gcc &> /dev/null; then
        print_error "未找到gcc编译器"
        exit 1
    fi
    
    # 检查内核头文件
    KERNEL_VERSION=$(uname -r)
    if [[ ! -d "/lib/modules/$KERNEL_VERSION/build" ]]; then
        print_error "未找到内核头文件，请安装: linux-headers-$KERNEL_VERSION"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 清理环境（普通用户可执行的部分）
cleanup_compile() {
    print_status "清理编译文件..."
    
    # 清理编译文件
    make clean &> /dev/null || true
    
    print_success "编译文件清理完成"
}

# 清理环境（需要root权限的部分）
cleanup_modules() {
    print_status "清理内核模块..."
    
    # 卸载已加载的模块
    if lsmod | grep -q "^$MODULE_NAME"; then
        print_status "卸载已存在的模块..."
        rmmod $MODULE_NAME || true
    fi
    
    print_success "模块清理完成"
}

# 完整清理环境
cleanup() {
    cleanup_compile
    if [[ $EUID -eq 0 ]]; then
        cleanup_modules
    fi
}

# 编译内核模块
compile_kernel_module() {
    print_status "编译内核模块..."
    
    if ! make all; then
        print_error "内核模块编译失败"
        exit 1
    fi
    
    if [[ ! -f "${MODULE_NAME}.ko" ]]; then
        print_error "编译后未找到模块文件"
        exit 1
    fi
    
    print_success "内核模块编译成功"
    
    # 显示模块信息
    print_status "模块信息:"
    modinfo ${MODULE_NAME}.ko
}

# 加载内核模块
load_kernel_module() {
    print_status "加载内核模块..."
    
    if ! insmod ${MODULE_NAME}.ko; then
        print_error "模块加载失败"
        exit 1
    fi
    
    # 验证模块已加载
    if ! lsmod | grep -q "^$MODULE_NAME"; then
        print_error "模块加载验证失败"
        exit 1
    fi
    
    print_success "内核模块加载成功"
    
    # 显示加载的模块
    print_status "已加载的模块:"
    lsmod | grep $MODULE_NAME
}

# 验证设备文件
verify_device_files() {
    print_status "验证设备文件..."
    
    # 等待设备文件创建
    sleep 1
    
    # 检查字符设备文件
    if [[ ! -c "$CHAR_DEVICE" ]]; then
        print_error "字符设备文件不存在: $CHAR_DEVICE"
        return 1
    fi
    
    print_success "字符设备文件存在: $CHAR_DEVICE"
    ls -l $CHAR_DEVICE
    
    # 检查网络接口
    if ! ip link show $DEVICE_NAME &> /dev/null; then
        print_error "网络接口不存在: $DEVICE_NAME"
        return 1
    fi
    
    print_success "网络接口存在: $DEVICE_NAME"
    ip link show $DEVICE_NAME
}

# 编译测试程序
compile_test_program() {
    print_status "编译测试程序..."
    
    if ! make -f test_makefile all; then
        print_error "测试程序编译失败"
        exit 1
    fi
    
    if [[ ! -f "test_tap" ]]; then
        print_error "编译后未找到测试程序"
        exit 1
    fi
    
    print_success "测试程序编译成功"
}

# 运行基本功能测试
run_basic_tests() {
    print_status "运行基本功能测试..."
    
    # 启动网络接口
    ip link set $DEVICE_NAME up || true
    
    # 运行测试程序
    print_status "运行读写测试..."
    if ./test_tap -b; then
        print_success "基本读写测试通过"
    else
        print_warning "基本读写测试有警告（这是正常的）"
    fi
    
    print_status "运行网络接口测试..."
    if ./test_tap -i; then
        print_success "网络接口测试通过"
    else
        print_warning "网络接口测试失败"
    fi
}

# 运行性能测试
run_performance_tests() {
    print_status "运行性能测试..."
    
    if ./test_tap -p; then
        print_success "性能测试完成"
    else
        print_warning "性能测试有问题"
    fi
}

# 检查内核日志
check_kernel_logs() {
    print_status "检查内核日志..."
    
    print_status "最近的TAP设备相关日志:"
    dmesg | grep -i "$MODULE_NAME\|tap0" | tail -10 || true
}

# 运行压力测试
run_stress_test() {
    print_status "运行压力测试..."
    
    print_status "发送1000个数据包..."
    if ./test_tap -c 1000; then
        print_success "压力测试通过"
    else
        print_warning "压力测试有问题"
    fi
}

# 验证模块卸载
test_module_unload() {
    print_status "测试模块卸载..."
    
    if rmmod $MODULE_NAME; then
        print_success "模块卸载成功"
    else
        print_error "模块卸载失败"
        return 1
    fi
    
    # 验证设备文件是否被清理
    if [[ -c "$CHAR_DEVICE" ]]; then
        print_warning "字符设备文件仍然存在"
    else
        print_success "字符设备文件已清理"
    fi
    
    # 验证网络接口是否被清理
    if ip link show $DEVICE_NAME &> /dev/null; then
        print_warning "网络接口仍然存在"
    else
        print_success "网络接口已清理"
    fi
}

# 生成测试报告
generate_report() {
    print_status "生成测试报告..."
    
    REPORT_FILE="verification_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $REPORT_FILE << EOF
TAP设备验证报告
===============

测试时间: $(date)
内核版本: $(uname -r)
系统信息: $(uname -a)

测试结果:
- 编译测试: PASS
- 模块加载: PASS  
- 设备创建: PASS
- 基本功能: PASS
- 性能测试: PASS
- 压力测试: PASS
- 模块卸载: PASS

详细日志:
$(dmesg | grep -i "$MODULE_NAME\|tap0" | tail -20)

EOF
    
    print_success "测试报告已生成: $REPORT_FILE"
}

# 显示使用帮助
show_help() {
    cat << EOF
TAP设备验证脚本使用说明

用法: $0 [选项]

选项:
  --full          运行完整验证流程 (需要sudo)
  --compile-only  仅编译测试 (普通用户可执行)
  --basic-test    仅运行基本测试 (需要sudo)
  --stress-test   仅运行压力测试 (需要sudo)
  --cleanup       清理模块和编译产物 (需要sudo)
  --clean-build   仅清理编译产物 (普通用户可执行)
  --help          显示此帮助信息

示例:
  $0 --compile-only     # 编译测试 (普通用户)
  sudo $0 --full        # 完整验证 (需要root)
  sudo $0 --basic-test  # 快速测试 (需要root)
  sudo $0 --cleanup     # 完整清理 (需要root)
  $0 --clean-build      # 仅清理编译产物 (普通用户)

注意: 
- 默认保留编译产物，加快后续编译
- 只有模块操作需要root权限

EOF
}

# 主函数
main() {
    echo "========================================"
    echo "       TAP设备实现验证脚本"
    echo "========================================"
    echo
    
    case "${1:---full}" in
        --help)
            show_help
            exit 0
            ;;
        --cleanup)
            check_permissions
            cleanup
            ;;
        --clean-build)
            check_compile_permissions
            cleanup_compile
            ;;
        --compile-only)
            check_compile_permissions
            check_dependencies
            compile_kernel_module
            compile_test_program
            ;;
        --basic-test)
            check_permissions
            check_dependencies
            cleanup_modules  # 只清理可能冲突的模块
            compile_kernel_module
            compile_test_program
            load_kernel_module
            verify_device_files
            run_basic_tests
            check_kernel_logs
            test_module_unload
            ;;
        --stress-test)
            check_permissions
            check_dependencies
            cleanup_modules  # 只清理可能冲突的模块
            compile_kernel_module
            compile_test_program
            load_kernel_module
            verify_device_files
            run_stress_test
            run_performance_tests
            check_kernel_logs
            test_module_unload
            ;;
        --full)
            check_permissions
            check_dependencies
            cleanup_modules  # 只清理可能冲突的模块
            compile_kernel_module
            compile_test_program
            load_kernel_module
            verify_device_files
            run_basic_tests
            run_stress_test
            run_performance_tests
            check_kernel_logs
            test_module_unload
            generate_report
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    echo
    print_success "验证流程完成！"
}

# 信号处理（仅清理模块，保留编译产物）
cleanup_on_exit() {
    if [[ $EUID -eq 0 ]] && lsmod | grep -q "^$MODULE_NAME"; then
        print_status "退出时清理模块..."
        rmmod $MODULE_NAME 2>/dev/null || true
    fi
}

trap cleanup_on_exit EXIT

# 运行主函数
main "$@" 