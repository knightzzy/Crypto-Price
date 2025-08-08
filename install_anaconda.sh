#!/bin/bash

# 加密货币监控系统安装脚本 - Anaconda环境优化版
# 作者: 量化开发专家
# 功能: 针对已安装Anaconda3的Ubuntu服务器优化部署
# 适用: Ubuntu 18.04+ 服务器环境 + Anaconda3

set -e  # 遇到错误立即退出

echo "=== 加密货币监控系统安装脚本 (Anaconda优化版) ==="
echo "开始时间: $(date)"
echo "系统信息: $(lsb_release -d | cut -f2)"

# 配置变量
REPO_URL="https://github.com/knightzzy/Crypto-Price.git"
PROJECT_NAME="Crypto-Price"
INSTALL_DIR="$HOME/crypto-monitor"
CONDA_ENV_NAME="crypto_monitor"

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

echo "1. 检查Anaconda环境..."

# 检查conda是否可用
if ! command -v conda &> /dev/null; then
    error_exit "未找到conda命令，请确保Anaconda3已正确安装并添加到PATH"
fi
success_msg "Anaconda3已安装 ($(conda --version))"

# 检查是否为root用户或有sudo权限
if [[ $EUID -eq 0 ]]; then
    SUDO_CMD=""
    success_msg "以root用户运行"
elif sudo -n true 2>/dev/null; then
    SUDO_CMD="sudo"
    success_msg "检测到sudo权限"
else
    warn_msg "没有sudo权限，将跳过系统依赖安装"
    SUDO_CMD=""
fi

# 更新系统包列表（如果有sudo权限）
if [ -n "$SUDO_CMD" ]; then
    echo "更新系统包列表..."
    $SUDO_CMD apt update || warn_msg "系统包列表更新失败"
fi

# 检查并安装git
if ! command -v git &> /dev/null; then
    if [ -n "$SUDO_CMD" ]; then
        echo "安装Git..."
        $SUDO_CMD apt install -y git || error_exit "Git安装失败"
    else
        error_exit "Git未安装且无sudo权限安装"
    fi
fi
success_msg "Git已安装 ($(git --version))"

# 安装系统依赖（如果有sudo权限）
if [ -n "$SUDO_CMD" ]; then
    echo "安装系统依赖包..."
    # 尝试不同的TA-Lib包名
    $SUDO_CMD apt install -y build-essential curl wget screen htop || warn_msg "部分系统依赖安装失败"
    
    # 尝试安装TA-Lib系统依赖（多种包名）
    echo "尝试安装TA-Lib系统依赖..."
    if $SUDO_CMD apt install -y libta-lib-dev; then
        success_msg "libta-lib-dev安装成功"
    elif $SUDO_CMD apt install -y ta-lib; then
        success_msg "ta-lib安装成功"
    else
        warn_msg "TA-Lib系统依赖安装失败，将使用conda安装"
    fi
else
    warn_msg "跳过系统依赖安装（无sudo权限）"
fi

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

echo "\n3. 设置Conda环境..."

# 初始化conda（确保在脚本中可用）
eval "$(conda shell.bash hook)"

# 检查环境是否已存在
if conda env list | grep -q "$CONDA_ENV_NAME"; then
    warn_msg "Conda环境 $CONDA_ENV_NAME 已存在"
    echo "是否删除现有环境并重新创建? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        conda env remove -n "$CONDA_ENV_NAME" -y
        success_msg "已删除现有环境"
    else
        info_msg "使用现有环境"
    fi
fi

# 创建conda环境
if ! conda env list | grep -q "$CONDA_ENV_NAME"; then
    echo "创建Conda环境..."
    conda create -n "$CONDA_ENV_NAME" python=3.9 -y || error_exit "无法创建Conda环境"
    success_msg "Conda环境创建成功"
fi

# 激活conda环境
echo "激活Conda环境..."
conda activate "$CONDA_ENV_NAME" || error_exit "无法激活Conda环境"
success_msg "Conda环境已激活"

echo "\n4. 安装Python依赖..."

# 升级pip
echo "升级pip..."
pip install --upgrade pip || warn_msg "pip升级失败，继续使用当前版本"

# 使用conda安装科学计算包（更稳定）
echo "使用conda安装科学计算包..."
conda install -y numpy pandas matplotlib seaborn || warn_msg "部分conda包安装失败"

# 使用pip安装其他依赖
echo "安装其他Python依赖..."
pip install requests loguru pyyaml python-dateutil orjson aiohttp || warn_msg "部分pip包安装失败"

# 尝试安装TA-Lib（多种方式）
echo "尝试安装TA-Lib技术指标库..."
if conda install -y -c conda-forge ta-lib; then
    success_msg "TA-Lib通过conda安装成功"
elif pip install TA-Lib; then
    success_msg "TA-Lib通过pip安装成功"
else
    warn_msg "TA-Lib安装失败，技术指标功能将不可用"
    warn_msg "可以稍后手动安装：conda install -c conda-forge ta-lib"
fi

echo "\n5. 检查配置文件..."

# 检查config.py是否存在
if [ ! -f "config.py" ]; then
    warn_msg "config.py配置文件不存在，将创建默认配置"
    if [ -f "config.py.example" ]; then
        cp config.py.example config.py
        success_msg "已从示例文件创建配置文件"
    else
        warn_msg "未找到示例配置文件，请手动配置config.py"
        info_msg "系统将使用默认配置继续安装，请稍后编辑config.py文件"
    fi
else
    success_msg "配置文件存在"
fi

echo "\n6. 设置文件权限..."

# 设置脚本执行权限
chmod +x *.py 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
success_msg "文件权限设置完成"

echo "\n7. 启动服务..."

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

# 获取服务器外网IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")

# 显示安装结果
echo "\n=== Anaconda环境安装完成 ==="
echo -e "${GREEN}Conda环境: $CONDA_ENV_NAME${NC}"
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
echo "  激活Conda环境: conda activate $CONDA_ENV_NAME"
echo "  查看监控日志: tail -f logs/monitor.log"
echo "  查看Dashboard日志: tail -f logs/dashboard.log"
echo "  实时监控日志: tail -f logs/monitor.log | grep -E '(买入|卖出|获利|止损)'"
echo "  停止监控服务: kill \$(cat monitor.pid)"
echo "  停止Dashboard: kill \$(cat dashboard.pid)"
echo "  重新部署: conda activate $CONDA_ENV_NAME && ./deploy.sh"
echo "  健康检查: ./health_check.sh"
echo "  查看进程状态: ps aux | grep -E '(start_monitor|web_dashboard)'"
echo "\n环境管理:"
echo "  查看conda环境: conda env list"
echo "  激活环境: conda activate $CONDA_ENV_NAME"
echo "  停用环境: conda deactivate"
echo "  删除环境: conda env remove -n $CONDA_ENV_NAME"
echo "  导出环境: conda env export -n $CONDA_ENV_NAME > environment.yml"
echo "\n防火墙配置 (如需要):"
echo "  开放8080端口: sudo ufw allow 8080"
echo "  查看防火墙状态: sudo ufw status"
echo "\nScreen会话管理 (推荐用于长期运行):"
echo "  创建监控会话: screen -S crypto_monitor"
echo "  在screen中运行: cd $INSTALL_DIR && conda activate $CONDA_ENV_NAME"
echo "  分离会话: Ctrl+A, D"
echo "  重新连接: screen -r crypto_monitor"
echo "  查看所有会话: screen -ls"
echo "\n更新代码:"
echo "  cd $INSTALL_DIR && git pull origin master && conda activate $CONDA_ENV_NAME && ./deploy.sh"

echo -e "\n${GREEN}🎉 Anaconda环境安装成功完成！${NC}"
echo "结束时间: $(date)"
echo -e "${YELLOW}提示: 建议使用conda环境管理和screen来管理长期运行的服务${NC}"
echo -e "${BLUE}如需帮助，请查看: $INSTALL_DIR/UBUNTU_DEPLOY.md${NC}"
echo -e "${BLUE}Anaconda用户专用指南: $INSTALL_DIR/ANACONDA_GUIDE.md${NC}"