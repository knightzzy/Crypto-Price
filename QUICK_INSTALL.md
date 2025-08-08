# 🚀 加密货币监控系统快速安装指南

## 📋 系统要求

- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- **内存**: 最低 1GB，推荐 2GB+
- **存储**: 最低 5GB 可用空间
- **网络**: 稳定的互联网连接
- **权限**: sudo 权限（用于安装系统依赖）
- **Python环境**: 支持系统Python 3.6+ 或 Anaconda3

## 🎯 选择安装方式

### 方式一：Anaconda用户（推荐）

如果您已安装Anaconda3，推荐使用专用安装脚本：

```bash
# 一键安装（Anaconda优化版）
curl -sSL https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install_anaconda.sh | bash

# 或手动下载执行
wget https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install_anaconda.sh
chmod +x install_anaconda.sh
./install_anaconda.sh
```

**Anaconda版本优势：**
- 🔧 更好的包管理和依赖解决
- 🏠 独立的conda环境隔离
- 📊 科学计算库预优化
- 🛠️ TA-Lib技术指标库稳定安装
- 🚀 更快的NumPy/Pandas性能

### 方式二：系统Python用户

如果使用系统Python环境：

```bash
# 一键安装命令
curl -sSL https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install.sh | bash
```

或者手动下载安装：

```bash
# 下载安装脚本
wget https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install.sh

# 添加执行权限
chmod +x install.sh

# 运行安装
./install.sh
```

## 🔧 安装过程

安装脚本会自动完成以下步骤：

1. **系统环境检查和安装**
   - 更新系统包列表
   - 安装 Git, Python3, pip3, python3-venv
   - 安装编译工具和系统依赖

2. **项目代码下载**
   - 从 GitHub 克隆最新代码
   - 安装到 `~/crypto-monitor` 目录

3. **Python 环境设置**
   - 创建独立的虚拟环境
   - 安装所有 Python 依赖包

4. **服务启动**
   - 启动加密货币监控服务
   - 启动 Web Dashboard (端口 8080)

5. **配置检查**
   - 验证服务运行状态
   - 显示访问地址和管理命令

## 🌐 访问 Web Dashboard

安装完成后，可以通过以下地址访问：

- **本地访问**: http://localhost:8080
- **远程访问**: http://YOUR_SERVER_IP:8080

## 📊 服务管理

### 查看服务状态
```bash
cd ~/crypto-monitor
ps aux | grep -E '(start_monitor|web_dashboard)'
```

### 查看实时日志
```bash
cd ~/crypto-monitor
# 监控服务日志
tail -f logs/monitor.log

# Web Dashboard 日志
tail -f logs/dashboard.log

# 只看交易信号
tail -f logs/monitor.log | grep -E '(买入|卖出|获利|止损)'
```

### 重启服务
```bash
cd ~/crypto-monitor
# 停止服务
kill $(cat monitor.pid)
kill $(cat dashboard.pid)

# 重新部署
./deploy.sh
```

## 🔄 更新代码

```bash
cd ~/crypto-monitor
git pull origin master
./deploy.sh
```

## 🛡️ 防火墙配置

如果需要远程访问 Web Dashboard：

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8080
sudo ufw status

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## 🖥️ 长期运行建议

### 使用 Screen (推荐)

```bash
# 创建 screen 会话
screen -S crypto_monitor

# 在 screen 中运行
cd ~/crypto-monitor
source venv/bin/activate
python start_monitor.py --mode enhanced

# 分离会话: Ctrl+A, D
# 重新连接: screen -r crypto_monitor
```

### 使用 Systemd 服务

```bash
cd ~/crypto-monitor

# 编辑服务文件，修改路径
sudo nano crypto-monitor.service
sudo nano crypto-dashboard.service

# 安装服务
sudo cp crypto-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable crypto-monitor crypto-dashboard
sudo systemctl start crypto-monitor crypto-dashboard

# 查看服务状态
sudo systemctl status crypto-monitor
sudo systemctl status crypto-dashboard
```

## 🔍 故障排除

### 常见问题

1. **端口 8080 被占用**
   ```bash
   sudo netstat -tulpn | grep :8080
   sudo kill -9 <PID>
   ```

2. **Python 依赖安装失败**
   ```bash
   cd ~/crypto-monitor
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **配置文件问题**
   ```bash
   cd ~/crypto-monitor
   cp config.py.example config.py
   nano config.py  # 编辑配置
   ```

4. **权限问题**
   ```bash
   cd ~/crypto-monitor
   chmod +x *.py *.sh
   ```

### 查看详细日志

```bash
cd ~/crypto-monitor

# 监控服务详细日志
tail -f logs/monitor.log

# 错误日志
grep -i error logs/monitor.log
grep -i error logs/dashboard.log
```

## 📞 获取帮助

- **详细文档**: [UBUNTU_DEPLOY.md](UBUNTU_DEPLOY.md)
- **健康检查**: `./health_check.sh`
- **GitHub Issues**: [提交问题](https://github.com/knightzzy/Crypto-Price/issues)

## 🎯 下一步

1. **配置交易参数**: 编辑 `config.py` 文件
2. **设置通知**: 配置 Telegram 或邮件通知
3. **监控性能**: 使用 `htop` 查看系统资源使用
4. **备份数据**: 定期备份 `crypto_monitor.db` 数据库文件

---

**🎉 恭喜！您的加密货币监控系统已成功安装并运行！**

访问 Web Dashboard 开始监控您的投资组合：http://YOUR_SERVER_IP:8080