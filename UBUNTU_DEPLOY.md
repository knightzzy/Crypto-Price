# Ubuntu服务器部署指南

## 系统要求
- Ubuntu 18.04+ (推荐 Ubuntu 20.04 LTS 或 22.04 LTS)
- 至少 1GB RAM
- 至少 2GB 可用磁盘空间
- 稳定的网络连接

## 快速部署

### 1. 克隆项目
```bash
# 克隆项目到服务器
git clone https://github.com/YOUR_USERNAME/laogao-monitoring.git
cd laogao-monitoring

# 给部署脚本执行权限
chmod +x deploy.sh
```

### 2. 一键部署
```bash
# 运行一键部署脚本
./deploy.sh
```

脚本会自动完成以下操作：
- ✅ 检查并安装系统依赖 (git, python3, pip3, python3-venv)
- ✅ 创建Python虚拟环境
- ✅ 安装Python依赖包
- ✅ 拉取最新代码
- ✅ 启动监控服务和Web Dashboard

### 3. 验证部署
```bash
# 检查服务状态
ps aux | grep -E '(start_monitor|web_dashboard)'

# 查看日志
tail -f logs/monitor.log
tail -f logs/dashboard.log

# 测试Web访问
curl http://localhost:8080
```

## 高级配置

### 使用Screen管理服务 (推荐)
```bash
# 创建screen会话
screen -S crypto_monitor

# 在screen中启动服务
./deploy.sh

# 分离screen会话 (Ctrl+A, D)
# 重新连接: screen -r crypto_monitor
# 查看所有会话: screen -ls
```

### 使用Systemd服务 (生产环境推荐)

#### 1. 修改服务配置文件
```bash
# 编辑监控服务配置
sudo nano crypto-monitor.service

# 修改以下路径为实际路径:
# WorkingDirectory=/your/actual/path/laogao-monitoring
# ExecStart=/your/actual/path/laogao-monitoring/venv/bin/python ...
# ReadWritePaths=/your/actual/path/laogao-monitoring

# 如果不是ubuntu用户，修改User和Group
```

#### 2. 安装systemd服务
```bash
# 复制服务文件
sudo cp crypto-monitor.service /etc/systemd/system/
sudo cp crypto-dashboard.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable crypto-monitor
sudo systemctl enable crypto-dashboard

# 启动服务
sudo systemctl start crypto-monitor
sudo systemctl start crypto-dashboard
```

#### 3. 管理systemd服务
```bash
# 查看服务状态
sudo systemctl status crypto-monitor
sudo systemctl status crypto-dashboard

# 重启服务
sudo systemctl restart crypto-monitor
sudo systemctl restart crypto-dashboard

# 停止服务
sudo systemctl stop crypto-monitor
sudo systemctl stop crypto-dashboard

# 查看日志
sudo journalctl -u crypto-monitor -f
sudo journalctl -u crypto-dashboard -f
```

### 防火墙配置
```bash
# 开放Web Dashboard端口
sudo ufw allow 8080

# 如果需要外网访问，确保安全配置
sudo ufw enable
sudo ufw status
```

### 反向代理配置 (可选)

#### 使用Nginx
```bash
# 安装nginx
sudo apt install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/crypto-monitor
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/crypto-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 监控和维护

### 日志管理
```bash
# 实时查看关键日志
tail -f logs/monitor.log | grep -E '(买入|卖出|获利|止损)'

# 日志轮转 (防止日志文件过大)
sudo nano /etc/logrotate.d/crypto-monitor
```

```
/home/ubuntu/laogao-monitoring/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### 健康检查脚本
```bash
# 创建健康检查脚本
cat > health_check.sh << 'EOF'
#!/bin/bash

# 检查监控进程
if ! pgrep -f "start_monitor.py" > /dev/null; then
    echo "$(date): 监控服务未运行，正在重启..." >> logs/health_check.log
    ./deploy.sh
fi

# 检查Web Dashboard
if ! curl -s http://localhost:8080 > /dev/null; then
    echo "$(date): Web Dashboard无响应" >> logs/health_check.log
fi
EOF

chmod +x health_check.sh
```

### 定时任务
```bash
# 添加定时健康检查
crontab -e

# 添加以下行 (每5分钟检查一次)
*/5 * * * * /home/ubuntu/laogao-monitoring/health_check.sh

# 每天凌晨重启服务 (可选)
0 2 * * * /home/ubuntu/laogao-monitoring/deploy.sh
```

## 更新代码
```bash
# 停止服务
kill $(cat monitor.pid) 2>/dev/null || true
kill $(cat dashboard.pid) 2>/dev/null || true

# 或者使用systemd
sudo systemctl stop crypto-monitor crypto-dashboard

# 拉取最新代码并重新部署
git pull origin master
./deploy.sh

# 或者重启systemd服务
sudo systemctl start crypto-monitor crypto-dashboard
```

## 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查日志
   tail -n 50 logs/monitor.log
   tail -n 50 logs/dashboard.log
   
   # 检查Python环境
   source venv/bin/activate
   python -c "import requests; print('OK')"
   ```

2. **端口被占用**
   ```bash
   # 查看端口占用
   sudo netstat -tulpn | grep 8080
   
   # 杀死占用进程
   sudo kill -9 PID
   ```

3. **权限问题**
   ```bash
   # 修复文件权限
   chmod +x *.py
   chmod +x deploy.sh
   
   # 修复目录权限
   chmod 755 logs/
   chmod 755 data/
   ```

4. **依赖安装失败**
   ```bash
   # 清理pip缓存
   pip cache purge
   
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

### 性能优化

1. **系统资源监控**
   ```bash
   # 安装htop
   sudo apt install htop
   
   # 监控资源使用
   htop
   ```

2. **数据库优化**
   ```bash
   # 定期清理旧数据 (保留30天)
   sqlite3 crypto_monitor.db "DELETE FROM notification_history WHERE timestamp < datetime('now', '-30 days');"
   sqlite3 crypto_monitor.db "VACUUM;"
   ```

## 安全建议

1. **更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **配置SSH密钥认证**
   ```bash
   # 禁用密码登录
   sudo nano /etc/ssh/sshd_config
   # PasswordAuthentication no
   sudo systemctl restart ssh
   ```

3. **设置防火墙**
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 8080
   sudo ufw enable
   ```

4. **定期备份**
   ```bash
   # 备份数据库和配置
   tar -czf backup_$(date +%Y%m%d).tar.gz crypto_monitor.db config.py logs/
   ```

## 联系支持

如果遇到问题，请提供以下信息：
- Ubuntu版本: `lsb_release -a`
- Python版本: `python3 --version`
- 错误日志: `tail -n 50 logs/monitor.log`
- 系统资源: `free -h && df -h`