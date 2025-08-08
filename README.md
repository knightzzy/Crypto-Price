# 🤖 加密货币价格监控系统

一个专业的加密货币价格监控系统，支持实时价格跟踪、智能预警和企业微信通知。专为定投策略设计，帮助您在最佳时机进行买卖操作。

## 📋 功能特性

### 🎯 核心功能
- **多币种监控**: 支持 RAY、CRV、PENDLE、CAKE 等主流DeFi代币
- **智能预警**: 基于价格变动百分比的分级预警系统
- **企业微信通知**: 实时推送买卖信号到企业微信群
- **数据持久化**: SQLite数据库存储历史价格和通知记录
- **异常检测**: 自动识别价格异常波动和市场异常

### 🔧 高级特性
- **配置化管理**: 支持自定义监控参数和阈值
- **配置自动重载**: 修改配置文件后无需重启程序，实时生效
- **风险控制**: 每日通知限制、紧急止损等风险管理功能
- **日志轮转**: 完善的日志记录和管理系统
- **重试机制**: API请求失败自动重试
- **冷却机制**: 避免同一币种频繁通知

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.7+：

```bash
python --version
```

### 2. 安装依赖

```bash
# 自动安装所有依赖
python start_monitor.py --install

# 或手动安装
pip install -r requirements.txt
```

### 3. 配置企业微信

1. 在企业微信中创建群聊机器人
2. 获取 webhook 地址
3. 修改 `config.py` 中的 `WECHAT_WEBHOOK` 配置

### 4. 测试连接

```bash
# 测试企业微信连接
python start_monitor.py --test

# 检查系统环境
python start_monitor.py --check
```

### 5. 启动监控

```bash
# 启动增强版监控（推荐）
python start_monitor.py --mode enhanced

# 启动基础版监控
python start_monitor.py --mode basic

# 直接启动（默认增强版）
python start_monitor.py
```

## ⚙️ 配置说明

### 主要配置项

在 `config.py` 中可以自定义以下配置：

```python
# 监控币种
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE"]

# 价格阈值（百分比）
PRICE_THRESHOLDS = {
    "buy_threshold": -5.0,      # 下跌5%提醒买入
    "major_buy": -15.0,         # 大跌15%强烈提醒买入
    "sell_threshold": 8.0,      # 上涨8%提醒卖出
    "major_sell": 20.0,         # 大涨20%强烈提醒卖出
}

# 监控频率
MONITOR_INTERVAL = 300  # 5分钟检查一次
NOTIFY_COOLDOWN = 3600  # 1小时通知冷却
```

### 🔄 配置自动重载功能

**重要特性**: 系统支持配置文件的实时重载，您可以：

- **实时配置更新**: 修改配置文件后无需重启程序
- **智能变化检测**: 自动检测配置文件修改时间
- **币种动态管理**: 实时添加或移除监控币种
- **变更通知**: 配置变更时自动发送企业微信通知
- **一次维护**: 只需修改config.py，系统自动应用新配置

**使用方法**:
1. 直接编辑 `config.py` 文件
2. 保存文件后系统会在下次检查周期自动检测变化
3. 新配置立即生效，无需手动重启
4. 系统会发送配置变更通知确认

**示例操作**:
```python
# 添加新币种到监控列表
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE", "BTC", "ETH"]

# 调整价格阈值
PRICE_THRESHOLDS = {
    "buy_threshold": -3.0,      # 改为下跌3%提醒
    "sell_threshold": 10.0,     # 改为上涨10%提醒
    # ... 其他配置
}
```

### 风险管理配置

```python
RISK_MANAGEMENT = {
    "max_daily_notifications": 20,   # 每日最大通知数
    "emergency_stop_loss": -30,      # 紧急止损阈值
    "profit_taking_levels": [10, 25, 50, 100]  # 分批获利点位
}
```

## 📊 监控逻辑

### 买入信号
- **普通买入**: 24小时跌幅 ≥ 5% 时提醒定投买入
- **加仓买入**: 24小时跌幅 ≥ 15% 时强烈建议加仓
- **抄底机会**: 24小时跌幅 ≥ 30% 时紧急止损提醒

### 卖出信号
- **部分获利**: 24小时涨幅 ≥ 8% 时提醒部分获利
- **获利了结**: 24小时涨幅 ≥ 20% 时强烈建议获利了结

### 通知示例

```
📉 RAY 价格下跌提醒
💰 当前价格: $2.1234
📊 24h跌幅: -6.78%
🛒 建议：可考虑定投买入
⏰ 时间: 2024-01-15 14:30:00
```

## 📁 文件结构

```
laogao-monitoring/
├── crypto_monitor.py      # 基础版监控程序
├── enhanced_monitor.py    # 增强版监控程序（推荐）
├── config.py             # 配置文件
├── start_monitor.py      # 启动脚本
├── requirements.txt      # 依赖包列表
├── README.md            # 使用说明
├── crypto_monitor.db    # SQLite数据库（自动创建）
└── crypto_monitor.log   # 日志文件（自动创建）
```

## 🛠️ 使用命令

### 启动器命令

```bash
# 显示帮助
python start_monitor.py --help

# 安装依赖
python start_monitor.py --install

# 检查系统状态
python start_monitor.py --status

# 检查环境
python start_monitor.py --check

# 测试webhook
python start_monitor.py --test

# 启动基础版
python start_monitor.py --mode basic

# 启动增强版
python start_monitor.py --mode enhanced
```

### 直接启动

```bash
# 基础版
python crypto_monitor.py

# 增强版
python enhanced_monitor.py
```

## 📈 数据存储

系统使用 SQLite 数据库存储以下数据：

- **价格历史**: 所有币种的历史价格数据
- **通知记录**: 发送的所有通知记录
- **配置信息**: 系统配置和状态信息

### 数据库表结构

```sql
-- 价格历史表
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    change_24h REAL,
    volume_24h REAL,
    market_cap REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 通知历史表
CREATE TABLE notification_history (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    message TEXT NOT NULL,
    price REAL NOT NULL,
    change_24h REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 自定义扩展

### 添加新币种

1. 在 `config.py` 中添加币种符号到 `MONITOR_SYMBOLS`
2. 在 `COIN_ID_MAPPING` 中添加对应的 CoinGecko ID

```python
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE", "UNI"]

COIN_ID_MAPPING = {
    "RAY": "raydium",
    "CRV": "curve-dao-token",
    "PENDLE": "pendle", 
    "CAKE": "pancakeswap-token",
    "UNI": "uniswap",  # 新添加
}
```

### 自定义通知模板

在 `config.py` 中修改 `MESSAGE_TEMPLATES`：

```python
MESSAGE_TEMPLATES = {
    "buy_signal": "📉 {symbol} 买入机会\n💰 价格: ${price:.4f}\n📊 24h: {change:.2f}%\n🛒 建议: 考虑定投",
    "sell_signal": "📈 {symbol} 卖出机会\n💰 价格: ${price:.4f}\n📊 24h: {change:.2f}%\n💸 建议: 考虑获利",
    # 可以添加更多模板
}
```

## 🚨 注意事项

### 安全提醒
- 请妥善保管企业微信 webhook 地址，避免泄露
- 定期备份数据库文件 `crypto_monitor.db`
- 建议在测试环境中先验证配置

### 性能优化
- 监控间隔不建议低于 60 秒，避免API限制
- 每日通知数量建议控制在 50 条以内
- 定期清理历史日志文件

### 风险提示
- 本系统仅提供价格监控和提醒功能
- 所有投资决策请基于个人判断
- 加密货币投资存在高风险，请谨慎投资

## 🐛 故障排除

### 常见问题

1. **无法获取价格数据**
   - 检查网络连接
   - 确认 CoinGecko API 可访问
   - 查看日志文件了解详细错误

2. **企业微信通知失败**
   - 验证 webhook 地址是否正确
   - 检查企业微信机器人是否正常
   - 运行测试命令：`python start_monitor.py --test`

3. **数据库错误**
   - 检查文件权限
   - 删除 `crypto_monitor.db` 重新初始化
   - 查看日志了解具体错误

### 日志查看

```bash
# 查看最新日志
tail -f crypto_monitor.log

# 查看错误日志
grep ERROR crypto_monitor.log
```

## 📞 技术支持

如果您在使用过程中遇到问题，请：

1. 查看日志文件 `crypto_monitor.log`
2. 运行系统检查：`python start_monitor.py --check`
3. 查看本文档的故障排除部分

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🔄 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持基础价格监控和企业微信通知
- 增强版支持数据持久化和异常检测
- 完整的配置管理和启动脚本

---

**免责声明**: 本软件仅用于教育和研究目的。使用本软件进行投资决策的风险由用户自行承担。开发者不对任何投资损失负责。