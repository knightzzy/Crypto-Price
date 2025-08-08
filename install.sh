#!/bin/bash

# 加密货币监控系统安装脚本 - Ubuntu服务器版本
# 作者: 量化开发专家
# 功能: 从零开始安装和部署加密货币监控系统
# 适用: Ubuntu 18.04+ 服务器环境

set -e  # 遇到错误立即退出

echo "=== 加密货币监控系统安装脚本 (Ubuntu服务器版) ==="
echo "开始时间: $(date)"
echo "系统信息: $(lsb_release -d | cut -f2)"

# 配置变量
REPO_URL="https://github.com/knightzzy/Crypto-Price.git"
PROJECT_NAME="Crypto-Price"
INSTALL_DIR="$HOME/crypto-monitor"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
error_exit() {
    echo -e "${RED}错误: $1${NC}" >&2
    echo "安装失败，脚本退出"
    exit 1
}

# 成功信息函数
success_msg() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 警告信息函数
warn_msg() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 信息函数
info_msg() {
    echo -e "${BLUE}ℹ $1${NC}"
}

echo "1. 检查和安装系统环境..."

# 检查是否为root用户或有sudo权限
if [[ $EUID -eq 0 ]]; then
    SUDO_CMD=""
    success_msg "以root用户运行"
elif sudo -n true 2>/dev/null; then
    SUDO_CMD="sudo"
    success_msg "检测到sudo权限"
else
    error_exit "需要root权限或sudo权限来安装系统依赖"
fi

# 更新系统包列表
echo "更新系统包列表..."
$SUDO_CMD apt update || error_exit "无法更新系统包列表"

# 检查并安装git
if ! command -v git &> /dev/null; then
    echo "安装Git..."
    $SUDO_CMD apt install -y git || error_exit "Git安装失败"
fi
success_msg "Git已安装 ($(git --version))"

# 检查并安装python3
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    $SUDO_CMD apt install -y python3 python3-dev || error_exit "Python3安装失败"
fi
success_msg "Python3已安装 ($(python3 --version))"

# 检查并安装pip3
if ! command -v pip3 &> /dev/null; then
    echo "安装pip3..."
    $SUDO_CMD apt install -y python3-pip || error_exit "pip3安装失败"
fi
success_msg "pip3已安装 ($(pip3 --version))"

# 安装python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo "安装python3-venv..."
    $SUDO_CMD apt install -y python3-venv || error_exit "python3-venv安装失败"
fi
success_msg "python3-venv已安装"

# 安装其他必要的系统依赖
echo "安装系统依赖包..."
$SUDO_CMD apt install -y build-essential curl wget screen htop || warn_msg "部分系统依赖安装失败，但不影响主要功能"

echo "\n2. 下载项目代码..."

# 如果安装目录已存在，询问是否删除
if [ -d "$INSTALL_DIR" ]; then
    warn_msg "安装目录 $INSTALL_DIR 已存在"
    echo "是否删除现有目录并重新安装? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        success_msg "已删除现有目录"
    else
        error_exit "安装取消"
    fi
fi

# 克隆项目
echo "从GitHub克隆项目..."
git clone "$REPO_URL" "$INSTALL_DIR" || error_exit "无法克隆项目"
success_msg "项目克隆成功"

# 进入项目目录
cd "$INSTALL_DIR" || error_exit "无法进入项目目录"
info_msg "当前目录: $(pwd)"

echo "\n3. 设置Python环境..."

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv || error_exit "无法创建虚拟环境"
success_msg "虚拟环境创建成功"

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate || error_exit "无法激活虚拟环境"
success_msg "虚拟环境已激活"

# 升级pip到最新版本
echo "升级pip到最新版本..."
pip install --upgrade pip || warn_msg "pip升级失败，继续使用当前版本"

# 安装依赖
echo "安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || error_exit "依赖安装失败"
    success_msg "依赖安装完成"
else
    error_exit "requirements.txt文件不存在"
fi

echo "\n4. 检查配置文件..."

# 检查config.py是否存在
if [ ! -f "config.py" ]; then
    error_exit "config.py配置文件不存在，请先配置"
fi
success_msg "配置文件存在"

echo "\n5. 设置文件权限..."

# 设置脚本执行权限
chmod +x *.py 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
success_msg "文件权限设置完成"

echo "\n6. 启动服务..."

# 创建必要的目录
mkdir -p logs
mkdir -p data

# 停止可能存在的旧服务
echo "检查并停止现有服务..."
pkill -f "start_monitor.py" 2>/dev/null || true
pkill -f "web_dashboard.py" 2>/dev/null || true
sleep 2

# 启动监控服务
echo "启动增强版监控服务..."
nohup python start_monitor.py --mode enhanced > logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > monitor.pid
sleep 5

# 检查监控服务是否启动成功
if kill -0 $MONITOR_PID 2>/dev/null; then
    success_msg "监控服务启动成功 (PID: $MONITOR_PID)"
else
    error_exit "监控服务启动失败，请检查logs/monitor.log"
fi

# 启动Web Dashboard
echo "启动Web Dashboard..."
nohup python web_dashboard.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > dashboard.pid
sleep 5

# 检查Web Dashboard是否启动成功
if kill -0 $DASHBOARD_PID 2>/dev/null; then
    success_msg "Web Dashboard启动成功 (PID: $DASHBOARD_PID)"
else
    warn_msg "Web Dashboard启动失败，请检查logs/dashboard.log"
fi

# 检查端口是否被占用
echo "检查服务端口状态..."
if command -v netstat &> /dev/null; then
    if netstat -tuln | grep -q ":8080"; then
        success_msg "Web Dashboard端口8080已监听"
    else
        warn_msg "Web Dashboard端口8080未监听，请检查服务状态"
    fi
fi

echo "\n7. 安装完成检查..."

# 检查数据库文件
if [ -f "crypto_monitor.db" ]; then
    success_msg "数据库文件存在"
else
    info_msg "数据库文件将在首次运行时创建"
fi

# 获取服务器外网IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

# 显示安装结果
echo "\n=== 安装完成 ==="
echo -e "${GREEN}监控服务PID: $MONITOR_PID${NC}"
echo -e "${GREEN}Web Dashboard PID: $DASHBOARD_PID${NC}"
echo -e "${BLUE}安装目录: $INSTALL_DIR${NC}"
echo -e "${BLUE}Web Dashboard访问地址:${NC}"
echo "  - 本地访问: http://localhost:8080"
echo "  - 服务器IP访问: http://$SERVER_IP:8080"
echo "\n日志文件位置:"
echo "  - 监控服务: $INSTALL_DIR/logs/monitor.log"
echo "  - Web Dashboard: $INSTALL_DIR/logs/dashboard.log"
echo "\n常用管理命令:"
echo "  进入项目目录: cd $INSTALL_DIR"
echo "  激活虚拟环境: source venv/bin/activate"
echo "  查看监控日志: tail -f logs/monitor.log"
echo "  查看Dashboard日志: tail -f logs/dashboard.log"
echo "  实时监控日志: tail -f logs/monitor.log | grep -E '(买入|卖出|获利|止损)'"
echo "  停止监控服务: kill \$(cat monitor.pid)"
echo "  停止Dashboard: kill \$(cat dashboard.pid)"
echo "  重新部署: ./deploy.sh"
echo "  健康检查: ./health_check.sh"
echo "  查看进程状态: ps aux | grep -E '(start_monitor|web_dashboard)'"
echo "\n防火墙配置 (如需要):"
echo "  开放8080端口: sudo ufw allow 8080"
echo "  查看防火墙状态: sudo ufw status"
echo "\nScreen会话管理 (推荐用于长期运行):"
echo "  创建监控会话: screen -S crypto_monitor"
echo "  在screen中运行: cd $INSTALL_DIR && source venv/bin/activate"
echo "  分离会话: Ctrl+A, D"
echo "  重新连接: screen -r crypto_monitor"
echo "  查看所有会话: screen -ls"
echo "\nSystemd服务配置 (可选):"
echo "  1. 编辑服务文件: sudo nano crypto-monitor.service"
echo "  2. 修改路径为: $INSTALL_DIR"
echo "  3. 复制服务文件: sudo cp crypto-*.service /etc/systemd/system/"
echo "  4. 启用服务: sudo systemctl enable crypto-monitor crypto-dashboard"
echo "  5. 启动服务: sudo systemctl start crypto-monitor crypto-dashboard"
echo "\n更新代码:"
echo "  cd $INSTALL_DIR && git pull origin master && ./deploy.sh"

echo -e "\n${GREEN}🎉 安装成功完成！${NC}"
echo "结束时间: $(date)"
echo -e "${YELLOW}提示: 建议使用screen或systemd来管理长期运行的服务${NC}"
echo -e "${BLUE}如需帮助，请查看: $INSTALL_DIR/UBUNTU_DEPLOY.md${NC}"