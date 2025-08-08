#!/bin/bash

# 健康检查脚本
# 功能: 自动检查服务状态，异常时重启服务
# 使用: 可配置为cron定时任务

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/health_check.log"
MAX_LOG_SIZE=10485760  # 10MB

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - ${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - ${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - ${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# 日志轮转
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        log_message "日志文件已轮转"
    fi
}

# 检查进程是否运行
check_process() {
    local process_name="$1"
    local description="$2"
    
    if pgrep -f "$process_name" > /dev/null; then
        return 0  # 进程运行中
    else
        return 1  # 进程未运行
    fi
}

# 检查端口是否监听
check_port() {
    local port="$1"
    local description="$2"
    
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            return 0  # 端口监听中
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            return 0  # 端口监听中
        fi
    fi
    
    return 1  # 端口未监听
}

# 检查HTTP服务
check_http() {
    local url="$1"
    local description="$2"
    
    if command -v curl &> /dev/null; then
        if curl -s --max-time 10 "$url" > /dev/null; then
            return 0  # HTTP服务正常
        fi
    elif command -v wget &> /dev/null; then
        if wget -q --timeout=10 --tries=1 "$url" -O /dev/null; then
            return 0  # HTTP服务正常
        fi
    fi
    
    return 1  # HTTP服务异常
}

# 重启服务
restart_services() {
    log_message "开始重启服务..."
    
    # 停止现有服务
    if [ -f "$SCRIPT_DIR/monitor.pid" ]; then
        local monitor_pid=$(cat "$SCRIPT_DIR/monitor.pid")
        if kill -0 "$monitor_pid" 2>/dev/null; then
            kill "$monitor_pid" || kill -9 "$monitor_pid"
            log_message "已停止监控服务 (PID: $monitor_pid)"
        fi
        rm -f "$SCRIPT_DIR/monitor.pid"
    fi
    
    if [ -f "$SCRIPT_DIR/dashboard.pid" ]; then
        local dashboard_pid=$(cat "$SCRIPT_DIR/dashboard.pid")
        if kill -0 "$dashboard_pid" 2>/dev/null; then
            kill "$dashboard_pid" || kill -9 "$dashboard_pid"
            log_message "已停止Dashboard服务 (PID: $dashboard_pid)"
        fi
        rm -f "$SCRIPT_DIR/dashboard.pid"
    fi
    
    # 强制清理残留进程
    pkill -f "start_monitor.py" 2>/dev/null || true
    pkill -f "web_dashboard.py" 2>/dev/null || true
    
    sleep 3
    
    # 重新启动服务
    cd "$SCRIPT_DIR"
    
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # 启动监控服务
    nohup python start_monitor.py --mode enhanced > logs/monitor.log 2>&1 &
    local monitor_pid=$!
    echo $monitor_pid > monitor.pid
    log_message "已启动监控服务 (PID: $monitor_pid)"
    
    sleep 3
    
    # 启动Dashboard服务
    nohup python web_dashboard.py > logs/dashboard.log 2>&1 &
    local dashboard_pid=$!
    echo $dashboard_pid > dashboard.pid
    log_message "已启动Dashboard服务 (PID: $dashboard_pid)"
    
    sleep 5
    
    # 验证服务启动
    if check_process "start_monitor.py" "监控服务"; then
        log_success "监控服务重启成功"
    else
        log_error "监控服务重启失败"
    fi
    
    if check_process "web_dashboard.py" "Dashboard服务"; then
        log_success "Dashboard服务重启成功"
    else
        log_error "Dashboard服务重启失败"
    fi
}

# 发送通知 (可选)
send_notification() {
    local message="$1"
    local level="$2"  # info, warning, error
    
    # 这里可以集成邮件、钉钉、企业微信等通知方式
    # 示例: 写入系统日志
    logger -t "crypto-monitor-health" "[$level] $message"
}

# 主检查函数
main_check() {
    local restart_needed=false
    local issues_found=()
    
    log_message "开始健康检查..."
    
    # 检查监控服务进程
    if ! check_process "start_monitor.py" "监控服务"; then
        log_warning "监控服务进程未运行"
        issues_found+=("监控服务进程")
        restart_needed=true
    else
        log_message "监控服务进程正常"
    fi
    
    # 检查Dashboard服务进程
    if ! check_process "web_dashboard.py" "Dashboard服务"; then
        log_warning "Dashboard服务进程未运行"
        issues_found+=("Dashboard服务进程")
        restart_needed=true
    else
        log_message "Dashboard服务进程正常"
    fi
    
    # 检查Dashboard端口
    if ! check_port "8080" "Dashboard端口"; then
        log_warning "Dashboard端口8080未监听"
        issues_found+=("Dashboard端口")
        restart_needed=true
    else
        log_message "Dashboard端口正常"
    fi
    
    # 检查HTTP服务
    if ! check_http "http://localhost:8080" "Dashboard HTTP服务"; then
        log_warning "Dashboard HTTP服务无响应"
        issues_found+=("Dashboard HTTP服务")
        restart_needed=true
    else
        log_message "Dashboard HTTP服务正常"
    fi
    
    # 检查数据库文件
    if [ ! -f "$SCRIPT_DIR/crypto_monitor.db" ]; then
        log_warning "数据库文件不存在"
        issues_found+=("数据库文件")
    else
        log_message "数据库文件存在"
    fi
    
    # 检查日志文件大小
    for log_file in "logs/monitor.log" "logs/dashboard.log"; do
        if [ -f "$SCRIPT_DIR/$log_file" ]; then
            local size=$(stat -f%z "$SCRIPT_DIR/$log_file" 2>/dev/null || stat -c%s "$SCRIPT_DIR/$log_file" 2>/dev/null || echo 0)
            if [ $size -gt 104857600 ]; then  # 100MB
                log_warning "日志文件 $log_file 过大 ($(($size / 1024 / 1024))MB)"
            fi
        fi
    done
    
    # 检查磁盘空间
    local disk_usage=$(df "$SCRIPT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "磁盘空间不足，使用率: ${disk_usage}%"
        send_notification "磁盘空间不足，使用率: ${disk_usage}%" "warning"
    fi
    
    # 检查内存使用
    if command -v free &> /dev/null; then
        local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$mem_usage" -gt 90 ]; then
            log_warning "内存使用率过高: ${mem_usage}%"
            send_notification "内存使用率过高: ${mem_usage}%" "warning"
        fi
    fi
    
    # 决定是否重启服务
    if [ "$restart_needed" = true ]; then
        log_error "发现问题: ${issues_found[*]}"
        send_notification "服务异常，正在重启: ${issues_found[*]}" "error"
        restart_services
        
        # 重启后再次检查
        sleep 10
        if check_process "start_monitor.py" && check_process "web_dashboard.py" && check_http "http://localhost:8080"; then
            log_success "服务重启后恢复正常"
            send_notification "服务重启成功" "info"
        else
            log_error "服务重启后仍有问题，需要人工干预"
            send_notification "服务重启失败，需要人工干预" "error"
        fi
    else
        log_success "所有服务运行正常"
    fi
    
    log_message "健康检查完成\n"
}

# 脚本入口
cd "$SCRIPT_DIR"

# 创建日志目录
mkdir -p logs

# 日志轮转
rotate_log

# 执行健康检查
main_check

# 如果是交互式运行，显示服务状态
if [ -t 1 ]; then
    echo "\n=== 当前服务状态 ==="
    echo "监控服务: $(check_process 'start_monitor.py' && echo '运行中' || echo '未运行')"
    echo "Dashboard服务: $(check_process 'web_dashboard.py' && echo '运行中' || echo '未运行')"
    echo "Dashboard端口: $(check_port '8080' && echo '监听中' || echo '未监听')"
    echo "HTTP服务: $(check_http 'http://localhost:8080' && echo '正常' || echo '异常')"
    echo "\n最近日志:"
    tail -n 5 "$LOG_FILE" 2>/dev/null || echo "无日志文件"
fi