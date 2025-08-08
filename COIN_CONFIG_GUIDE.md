# 💰 币种配置简易指南

## 📋 快速配置步骤

### 1. 修改监控币种列表

在 `config.py` 文件中找到 `MONITOR_SYMBOLS`，修改您要监控的币种：

```python
# 当前配置
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE", "BLUE", "NXPC"]

# 修改示例 - 只监控主流币种
MONITOR_SYMBOLS = ["BTC", "ETH", "BNB", "SOL"]
```

### 2. 更新币种ID映射

**重要**: 如果添加新币种，必须在 `COIN_ID_MAPPING` 中添加对应的CoinGecko ID：

```python
COIN_ID_MAPPING = {
    # 原有币种
    "RAY": "raydium",
    "CRV": "curve-dao-token", 
    "PENDLE": "pendle",
    "CAKE": "pancakeswap-token",
    
    # 新增币种 - 必须添加对应的CoinGecko ID
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "BLUE": "blue-protocol",
    "NXPC": "nxpc",  # 请确认正确的ID
}
```

## 🔍 如何查找CoinGecko ID

1. 访问 [CoinGecko](https://www.coingecko.com/)
2. 搜索您要的币种
3. 查看URL中的ID，例如：
   - `https://www.coingecko.com/en/coins/bitcoin` → ID是 `bitcoin`
   - `https://www.coingecko.com/en/coins/ethereum` → ID是 `ethereum`

## 📊 常用币种配置

### 主流币种
```python
MONITOR_SYMBOLS = ["BTC", "ETH", "BNB", "SOL", "ADA"]

COIN_ID_MAPPING = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "BNB": "binancecoin",
    "SOL": "solana",
    "ADA": "cardano",
}
```

### DeFi币种
```python
MONITOR_SYMBOLS = ["UNI", "AAVE", "COMP", "MKR", "CRV"]

COIN_ID_MAPPING = {
    "UNI": "uniswap",
    "AAVE": "aave",
    "COMP": "compound-governance-token",
    "MKR": "maker",
    "CRV": "curve-dao-token",
}
```

### 当前您的配置
```python
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE", "BLUE", "NXPC", "BTC"]

COIN_ID_MAPPING = {
    "RAY": "raydium",
    "CRV": "curve-dao-token", 
    "PENDLE": "pendle",
    "CAKE": "pancakeswap-token",
    "BLUE": "blue-protocol",      # ⚠️ 已停止交易
    "NXPC": "nexpace",            # ✅ 已修正
    "BTC": "bitcoin",             # ✅ 已添加
}
```

### ⚠️ 特殊说明

**BLUE币种问题**: 根据CoinGecko数据，BLUE (Blue Protocol) 已经停止交易8天，这可能导致无法获取价格数据。建议：
- 如果不需要监控BLUE，可以从MONITOR_SYMBOLS中移除
- 或者等待该币种恢复交易

**配置生效时间**: 系统每5分钟检查一次配置变化，修改后请耐心等待下一个检查周期。

## ⚠️ 重要提醒

1. **必须同步修改**: `MONITOR_SYMBOLS` 中的每个币种都必须在 `COIN_ID_MAPPING` 中有对应的ID

2. **ID准确性**: 错误的CoinGecko ID会导致无法获取价格数据

3. **保存生效**: 修改后保存文件，系统会自动检测并应用新配置（无需重启）

4. **测试验证**: 可以运行 `python quick_test_reload.py` 测试配置是否正确

## 🚀 配置示例

如果您想监控 BTC、ETH、RAY、PENDLE，配置如下：

```python
# 第一步：修改监控列表
MONITOR_SYMBOLS = ["BTC", "ETH", "RAY", "PENDLE"]

# 第二步：确保ID映射完整
COIN_ID_MAPPING = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "RAY": "raydium",
    "PENDLE": "pendle",
}
```

保存文件后，系统会自动更新监控币种，您会收到企业微信通知确认变更！🎉