#!/bin/bash
#
# Typora 工作空间监控服务安装脚本
#
# 支持：
#   - Linux (systemd)
#   - macOS (launchd)
#
# 使用方式：
#   sudo ./install-service.sh install          # 安装服务
#   sudo ./install-service.sh uninstall        # 卸载服务
#   sudo ./install-service.sh start            # 启动服务
#   sudo ./install-service.sh stop             # 停止服务
#   sudo ./install-service.sh status           # 查看状态
#   sudo ./install-service.sh restart          # 重启服务
#   sudo ./install-service.sh logs             # 查看日志
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取 typora 根目录（service-install 的上一级）
TYPORA_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="typora-watch"
PYTHON_BIN="${PYTHON_BIN:-python3}"
# watch_workspace.py 在 scripts 目录下
WATCH_SCRIPT="${TYPORA_ROOT}/scripts/watch_workspace.py"
WORKSPACE="${TYPORA_WORKSPACE:-}"

# systemd 配置
SYSTEMD_SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# launchd 配置（使用 LaunchAgent 而非 LaunchDaemon，以用户身份运行）
LAUNCHD_AGENT_DIR="$HOME/Library/LaunchAgents"
LAUNCHD_PLIST_FILE="${LAUNCHD_AGENT_DIR}/com.typora.watch.plist"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测是否以 root 身份运行
is_root() {
    [[ $EUID -eq 0 ]]
}

# 获取非 root 用户信息
get_real_user() {
    if is_root; then
        echo "${SUDO_USER:-$USER}"
    else
        echo "$USER"
    fi
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    # 检测虚拟环境
    VENV_DIR="${TYPORA_ROOT}/venv"
    VENV_PYTHON="${VENV_DIR}/bin/python"

    if [[ -f "$VENV_PYTHON" ]]; then
        log_info "检测到虚拟环境，使用: $VENV_PYTHON"
        PYTHON_BIN="$VENV_PYTHON"
    elif ! command -v "$PYTHON_BIN" &> /dev/null; then
        log_error "Python 未找到: $PYTHON_BIN"
        log_info "请安装 Python 或设置 PYTHON_BIN 环境变量"
        exit 1
    fi

    # 检查 watchdog（仅检查，不自动安装）
    if ! "$PYTHON_BIN" -c "import watchdog" &> /dev/null; then
        log_error "未安装 watchdog 库"
        log_info "请先安装 watchdog:"
        log_info "  cd $TYPORA_ROOT"
        log_info "  source venv/bin/activate  # 如果使用虚拟环境"
        log_info "  pip install watchdog"
        exit 1
    fi

    log_info "依赖检查完成"
}

# 获取工作空间路径
get_workspace() {
    if [[ -z "$WORKSPACE" ]]; then
        read -p "请输入 Typora 工作空间路径: " WORKSPACE
    fi

    if [[ ! -d "$WORKSPACE" ]]; then
        log_error "工作空间路径不存在: $WORKSPACE"
        exit 1
    fi

    echo "$WORKSPACE"
}

# 安装 systemd 服务
install_systemd() {
    log_info "安装 systemd 服务..."

    check_dependencies
    WORKSPACE=$(get_workspace)

    log_info "使用工作目录: $WORKSPACE"

    sudo tee "$SYSTEMD_SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Typora Workspace File Watcher
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$TYPORA_ROOT
Environment="TYPORA_WORKSPACE=$WORKSPACE"
ExecStart=$($PYTHON_BIN -c "import sys; print(sys.executable)") $WATCH_SCRIPT
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"

    log_info "systemd 服务安装完成"
    log_info "服务状态: $(sudo systemctl is-active $SERVICE_NAME)"
}

# 卸载 systemd 服务
uninstall_systemd() {
    log_info "卸载 systemd 服务..."

    if [[ -f "$SYSTEMD_SERVICE_FILE" ]]; then
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "$SYSTEMD_SERVICE_FILE"
        sudo systemctl daemon-reload
        log_info "systemd 服务已卸载"
    else
        log_warn "服务未安装"
    fi
}

# 安装 launchd 服务（使用 LaunchAgent）
install_launchd() {
    log_info "安装 launchd 服务（LaunchAgent）..."

    # 检查是否以 root 身份运行
    if is_root; then
        log_warn "检测到使用 sudo 运行脚本"
        log_warn "LaunchAgent 是用户级服务，不应使用 sudo 安装"
        log_warn "建议退出 root 模式后重新运行："
        log_warn "  ./install-service.sh install"
        log_warn ""
        log_warn "如果继续，可能导致文件权限问题"
        read -p "是否继续? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "取消安装"
            return 1
        fi
        # 获取实际用户的信息
        REAL_USER=$(get_real_user)
        if [[ -n "$REAL_USER" && "$REAL_USER" != "root" ]]; then
            LAUNCHD_AGENT_DIR="/Users/$REAL_USER/Library/LaunchAgents"
            LAUNCHD_PLIST_FILE="${LAUNCHD_AGENT_DIR}/com.typora.watch.plist"
            log_info "使用用户目录: $LAUNCHD_AGENT_DIR"
        fi
    fi

    check_dependencies
    WORKSPACE=$(get_workspace)

    log_info "使用工作目录: $WORKSPACE"

    # 创建 LaunchAgents 目录
    mkdir -p "$LAUNCHD_AGENT_DIR"

    # 日志文件路径（用户目录）
    local log_dir="$HOME/.typora-ext-logs"

    # 检查并修复日志目录权限
    if [[ -d "$log_dir" ]]; then
        # 获取目录所有者的 UID
        local owner=$(stat -f '%u' "$log_dir" 2>/dev/null || stat -c '%u' "$log_dir" 2>/dev/null)
        # 获取实际用户的 UID（不是 root 的 UID）
        local target_uid=$(id -u "$(get_real_user)")
        if [[ "$owner" != "$target_uid" ]]; then
            log_warn "日志目录权限不正确，正在修复..."
            log_warn "  当前所有者 UID: $owner"
            log_warn "  应该所有者 UID: $target_uid"
            rm -rf "$log_dir"
            mkdir -p "$log_dir"
            log_info "日志目录已修复"
        fi
    else
        mkdir -p "$log_dir"
    fi

    # 创建 plist 文件
    cat > "$LAUNCHD_PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.typora.watch</string>

    <key>ProgramArguments</key>
    <array>
        <string>$($PYTHON_BIN -c "import sys; print(sys.executable)")</string>
        <string>$WATCH_SCRIPT</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>TYPORA_WORKSPACE</key>
        <string>$WORKSPACE</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>$TYPORA_ROOT</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>

    <key>StandardOutPath</key>
    <string>/dev/null</string>

    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>
EOF

    chmod 644 "$LAUNCHD_PLIST_FILE"

    # 卸载旧版本（如果存在）
    launchctl bootout gui/"$(id -u "$(get_real_user)")"/com.typora.watch 2>/dev/null || true
    launchctl unload "$LAUNCHD_PLIST_FILE" 2>/dev/null || true

    # 使用 launchctl bootstrap 加载并启动服务（推荐方式）
    # 注意：bootstrap 需要使用域格式：gui/uid/label
    local target_user=$(get_real_user)
    local target_uid=$(id -u "$target_user")

    launchctl bootstrap "gui/$target_uid" "$LAUNCHD_PLIST_FILE"

    log_info "launchd 服务安装完成"
    log_info "服务状态: $(launchctl list | grep com.typora.watch || echo '未运行')"
    log_info "日志目录: $log_dir"
}

# 卸载 launchd 服务（LaunchAgent）
uninstall_launchd() {
    log_info "卸载 launchd 服务..."

    if [[ -f "$LAUNCHD_PLIST_FILE" ]]; then
        # 使用 bootout 卸载（推荐方式）
        local target_user=$(get_real_user)
        local target_uid=$(id -u "$target_user")
        launchctl bootout "gui/$target_uid/com.typora.watch" 2>/dev/null || true
        # 旧方式兼容
        launchctl unload -w "$LAUNCHD_PLIST_FILE" 2>/dev/null || true
        rm -f "$LAUNCHD_PLIST_FILE"
        log_info "launchd 服务已卸载"
    else
        log_warn "服务未安装"
    fi

    # 同时卸载旧的 LaunchDaemon 版本（如果存在）
    local old_plist="/Library/LaunchDaemons/com.typora.watch.plist"
    if [[ -f "$old_plist" ]]; then
        log_info "检测到旧版本 LaunchDaemon，正在卸载..."
        sudo launchctl unload -w "$old_plist" 2>/dev/null || true
        sudo rm -f "$old_plist"
        log_info "旧版本已卸载"
    fi
}

# 安装服务
install_service() {
    case $OS in
        linux)
            install_systemd
            ;;
        macos)
            install_launchd
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 卸载服务
uninstall_service() {
    case $OS in
        linux)
            uninstall_systemd
            ;;
        macos)
            uninstall_launchd
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 启动服务
start_service() {
    case $OS in
        linux)
            sudo systemctl start "$SERVICE_NAME"
            log_info "服务已启动"
            ;;
        macos)
            launchctl start "com.typora.watch"
            log_info "服务已启动"
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 停止服务
stop_service() {
    case $OS in
        linux)
            sudo systemctl stop "$SERVICE_NAME"
            log_info "服务已停止"
            ;;
        macos)
            launchctl stop "com.typora.watch"
            log_info "服务已停止"
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 查看状态
status_service() {
    case $OS in
        linux)
            sudo systemctl status "$SERVICE_NAME"
            ;;
        macos)
            launchctl list | grep -i typora || echo "服务未运行"
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 查看日志
logs_service() {
    case $OS in
        linux)
            sudo journalctl -u "$SERVICE_NAME" -f
            ;;
        macos)
            local log_dir="$HOME/.typora-ext-logs"
            log_info "日志目录: $log_dir"
            if [[ -f "$log_dir/typora-watch.log" ]]; then
                tail -f "$log_dir/typora-watch.log"
            else
                log_warn "日志文件不存在"
            fi
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 重启服务
restart_service() {
    stop_service
    sleep 1
    start_service
}

# 主函数
main() {
    case "${1:-}" in
        install)
            install_service
            ;;
        uninstall)
            uninstall_service
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        logs)
            logs_service
            ;;
        *)
            echo "用法: $0 {install|uninstall|start|stop|restart|status|logs}"
            echo ""
            echo "命令:"
            echo "  install    安装并启动服务"
            echo "  uninstall  停止并卸载服务"
            echo "  start      启动服务"
            echo "  stop       停止服务"
            echo "  restart    重启服务"
            echo "  status     查看服务状态"
            echo "  logs       查看服务日志"
            echo ""
            echo "环境变量:"
            echo "  TYPORA_WORKSPACE  Typora 工作空间路径"
            echo "  PYTHON_BIN        Python 可执行文件 (默认: python3)"
            exit 1
            ;;
    esac
}

main "$@"
