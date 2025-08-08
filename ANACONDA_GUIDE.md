# Anaconda环境加密货币监控系统使用指南

## 📋 概述

本指南专门为已安装Anaconda3的用户提供详细的部署和使用说明。Anaconda环境具有更好的包管理和环境隔离能力，特别适合科学计算和数据分析应用。

## 🚀 快速开始

### 1. 使用专用安装脚本

```bash
# 下载并运行Anaconda优化版安装脚本
curl -sSL https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install_anaconda.sh | bash

# 或者手动下载后执行
wget https://raw.githubusercontent.com/knightzzy/Crypto-Price/master/install_anaconda.sh
chmod +x install_anaconda.sh
./install_anaconda.sh
```

### 2. 手动安装步骤

如果自动安装脚本遇到问题，可以按以下步骤手动安装：

```bash
# 1. 克隆项目
git clone https://github.com/knightzzy/Crypto-Price.git
cd Crypto-Price

# 2. 创建conda环境
conda create -n crypto_monitor python=3.9 -y
conda activate crypto_monitor

# 3. 安装科学计算包
conda install -y numpy pandas matplotlib seaborn

# 4. 安装TA-Lib技术指标库
conda install -y -c conda-forge ta-lib

# 5. 安装其他依赖
pip install requests loguru pyyaml python-dateutil orjson aiohttp

# 6. 配置文件
cp config.py.example config.py
# 编辑config.py文件，配置企业微信机器人等

# 7. 启动服务
python start_monitor.py --mode enhanced
```

## 🔧 环境管理

### Conda环境操作

```bash
# 查看所有环境
conda env list

# 激活环境
conda activate crypto_monitor

# 停用环境
conda deactivate

# 删除环境
conda env remove -n crypto_monitor

# 导出环境配置
conda env export -n crypto_monitor > environment.yml

# 从配置文件创建环境
conda env create -f environment.yml
```

### 包管理

```bash
# 查看已安装的包
conda list

# 安装新包（优先使用conda）
conda install package_name

# 使用pip安装（conda没有的包）
pip install package_name

# 更新包
conda update package_name

# 更新所有包
conda update --all
```

## 📊 技术指标库配置

### TA-Lib安装

TA-Lib是专业的技术分析库，在Anaconda环境中安装更加稳定：

```bash
# 方法1：使用conda-forge（推荐）
conda install -c conda-forge ta-lib

# 方法2：如果方法1失败，尝试pip
pip install TA-Lib

# 验证安装
python -c "import talib; print('TA-Lib版本:', talib.__version__)"
```

### 常用技术指标示例

```python
import talib
import numpy as np

# 示例价格数据
prices = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])

# 移动平均线
ma5 = talib.SMA(prices, timeperiod=5)
ma10 = talib.SMA(prices, timeperiod=10)

# RSI相对强弱指标
rsi = talib.RSI(prices, timeperiod=14)

# MACD指标
macd, macdsignal, macdhist = talib.MACD(prices)

# 布林带
upper, middle, lower = talib.BBANDS(prices, timeperiod=20)
```

## 🖥️ 服务管理

### 启动服务

```bash
# 进入项目目录
cd ~/crypto-monitor

# 激活环境
conda activate crypto_monitor

# 启动监控服务（后台运行）
nohup python start_monitor.py --mode enhanced > logs/monitor.log 2>&1 &

# 启动Web Dashboard
nohup python web_dashboard.py > logs/dashboard.log 2>&1 &
```

### 使用Screen管理长期运行服务

```bash
# 创建screen会话
screen -S crypto_monitor

# 在screen中激活环境并启动服务
conda activate crypto_monitor
cd ~/crypto-monitor
python start_monitor.py --mode enhanced

# 分离会话（服务继续运行）
# 按 Ctrl+A，然后按 D

# 重新连接会话
screen -r crypto_monitor

# 查看所有会话
screen -ls

# 终止会话
screen -S crypto_monitor -X quit
```

### 服务状态检查

```bash
# 检查进程状态
ps aux | grep -E '(start_monitor|web_dashboard)'

# 检查端口占用
netstat -tuln | grep 8080

# 查看实时日志
tail -f logs/monitor.log
tail -f logs/dashboard.log

# 查看交易信号日志
tail -f logs/monitor.log | grep -E '(买入|卖出|获利|止损)'
```

## 📈 性能优化

### 内存优化

```python
# 在config.py中配置
PERFORMANCE_CONFIG = {
    'max_history_days': 30,  # 减少历史数据保存天数
    'batch_size': 100,       # 批处理大小
    'cache_size': 1000,      # 缓存大小
    'gc_interval': 3600,     # 垃圾回收间隔（秒）
}
```

### 并行计算

```python
# 使用NumPy向量化计算
import numpy as np

# 批量计算技术指标
def calculate_indicators_batch(price_data):
    # 向量化计算，避免循环
    ma5 = np.convolve(price_data, np.ones(5)/5, mode='valid')
    ma20 = np.convolve(price_data, np.ones(20)/20, mode='valid')
    return ma5, ma20
```

## 🔍 故障排除

### 常见问题

#### 1. TA-Lib安装失败

```bash
# 解决方案1：更新conda
conda update conda
conda install -c conda-forge ta-lib

# 解决方案2：使用mamba（更快的包管理器）
conda install mamba -c conda-forge
mamba install -c conda-forge ta-lib

# 解决方案3：手动编译安装
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

#### 2. 环境激活失败

```bash
# 初始化conda
conda init bash
source ~/.bashrc

# 或者手动激活
source ~/anaconda3/etc/profile.d/conda.sh
conda activate crypto_monitor
```

#### 3. 包冲突问题

```bash
# 清理conda缓存
conda clean --all

# 重新创建环境
conda env remove -n crypto_monitor
conda create -n crypto_monitor python=3.9 -y
```

#### 4. 内存不足

```bash
# 检查内存使用
free -h
top -p $(pgrep -f start_monitor)

# 优化配置
# 在config.py中减少监控频率和历史数据量
MONITOR_INTERVAL = 60  # 增加到60秒
MAX_HISTORY_DAYS = 7   # 减少到7天
```

### 日志分析

```bash
# 查看错误日志
grep -i error logs/monitor.log
grep -i exception logs/monitor.log

# 查看性能统计
grep -i "memory\|cpu\|performance" logs/monitor.log

# 查看交易信号
grep -E "(买入|卖出|信号)" logs/monitor.log | tail -20
```

## 📊 数据科学扩展

### Jupyter Notebook集成

```bash
# 在crypto_monitor环境中安装Jupyter
conda activate crypto_monitor
conda install jupyter notebook ipykernel

# 注册内核
python -m ipykernel install --user --name crypto_monitor --display-name "Crypto Monitor"

# 启动Jupyter
jupyter notebook
```

### 数据分析示例

```python
# 在Jupyter中分析交易数据
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 读取交易日志
df = pd.read_csv('data/trading_history.csv')

# 绘制收益曲线
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['cumulative_return'])
plt.title('累计收益曲线')
plt.xlabel('时间')
plt.ylabel('累计收益率')
plt.show()

# 分析胜率
win_rate = (df['return'] > 0).mean()
print(f'胜率: {win_rate:.2%}')
```

## 🔄 自动化部署

### 创建部署脚本

```bash
#!/bin/bash
# auto_deploy.sh - 自动化部署脚本

set -e

echo "开始自动化部署..."

# 激活环境
source ~/anaconda3/etc/profile.d/conda.sh
conda activate crypto_monitor

# 进入项目目录
cd ~/crypto-monitor

# 停止现有服务
pkill -f "start_monitor.py" || true
pkill -f "web_dashboard.py" || true
sleep 5

# 更新代码
git pull origin master

# 更新依赖
conda env update -f environment.yml

# 重启服务
nohup python start_monitor.py --mode enhanced > logs/monitor.log 2>&1 &
nohup python web_dashboard.py > logs/dashboard.log 2>&1 &

echo "部署完成！"
```

### 定时任务

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点自动更新
0 2 * * * /home/username/crypto-monitor/auto_deploy.sh >> /home/username/crypto-monitor/logs/deploy.log 2>&1

# 每小时检查服务状态
0 * * * * /home/username/crypto-monitor/health_check.sh
```

## 📚 进阶配置

### 多环境管理

```bash
# 开发环境
conda create -n crypto_dev python=3.9
conda activate crypto_dev
# 安装开发依赖...

# 生产环境
conda create -n crypto_prod python=3.9
conda activate crypto_prod
# 安装生产依赖...

# 测试环境
conda create -n crypto_test python=3.9
conda activate crypto_test
# 安装测试依赖...
```

### 配置文件管理

```bash
# 不同环境的配置文件
config_dev.py    # 开发环境配置
config_prod.py   # 生产环境配置
config_test.py   # 测试环境配置

# 使用环境变量切换
export CRYPTO_ENV=prod
python start_monitor.py --config config_${CRYPTO_ENV}.py
```

## 🎯 最佳实践

1. **环境隔离**：为不同项目创建独立的conda环境
2. **版本固定**：使用environment.yml固定包版本
3. **日志管理**：定期清理和归档日志文件
4. **监控告警**：设置系统资源监控和告警
5. **备份策略**：定期备份配置文件和交易数据
6. **安全配置**：保护API密钥和敏感配置
7. **性能调优**：根据服务器资源调整参数
8. **文档维护**：及时更新配置和使用文档

## 📞 技术支持

如果在使用过程中遇到问题，可以：

1. 查看日志文件：`logs/monitor.log` 和 `logs/dashboard.log`
2. 检查GitHub Issues：https://github.com/knightzzy/Crypto-Price/issues
3. 参考官方文档：README.md 和其他指南文档
4. 社区讨论：在项目讨论区提问

---

**注意**：本指南基于Anaconda3环境，如果使用其他Python环境，请参考相应的安装指南。