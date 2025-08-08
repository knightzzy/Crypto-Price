#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币监控系统配置文件
用户可以在此文件中自定义监控参数
"""

# ==================== 基础配置 ====================

# 企业微信机器人webhook地址
WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=46e4e50e-8aa7-4b2f-8983-41800deafa5f"

# 要监控的币种列表
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE", "NXPC"]

# ==================== 价格阈值配置 ====================

# 价格变动阈值（百分比）
# 正数表示上涨，负数表示下跌
PRICE_THRESHOLDS = {
    # 买入信号阈值
    "buy_threshold": -5.0,      # 下跌5%时提醒买入
    "major_buy": -15.0,         # 大跌15%时强烈提醒买入
    
    # 卖出信号阈值  
    "sell_threshold": 8.0,      # 上涨8%时提醒卖出
    "major_sell": 20.0,         # 大涨20%时强烈提醒卖出
}

# ==================== 监控频率配置 ====================

# 价格检查间隔（秒）
MONITOR_INTERVAL = 300  # 5分钟检查一次

# 通知冷却时间（秒）- 避免同一币种频繁通知
NOTIFY_COOLDOWN = 3600  # 1小时

# ==================== API配置 ====================

# CoinGecko API配置
API_CONFIG = {
    "base_url": "https://api.coingecko.com/api/v3",
    "timeout": 10,
    "retry_times": 3,
    "retry_delay": 5
}

# 币种ID映射（CoinGecko API使用的ID）
COIN_ID_MAPPING = {
    "RAY": "raydium",
    "CRV": "curve-dao-token", 
    "PENDLE": "pendle",
    "CAKE": "pancakeswap-token",
    "NXPC": "nexpace", 
    # 可以添加更多币种
    # "ETH": "ethereum",
    # "BNB": "binancecoin",
    # "BLUE": "blue-protocol",  # 已停止交易
}

# ==================== 日志配置 ====================

LOG_CONFIG = {
    "level": "INFO",
    "file_name": "crypto_monitor.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# ==================== 高级配置 ====================

# 价格异常检测
ANOMALY_DETECTION = {
    "enable": True,
    "volume_spike_threshold": 200,  # 成交量异常倍数
    "price_spike_threshold": 50,    # 价格异常变动百分比
}

# 风险管理
RISK_MANAGEMENT = {
    "max_daily_notifications": 20,   # 每日最大通知数量
    "emergency_stop_loss": -30,      # 紧急止损阈值
    "profit_taking_levels": [10, 25, 50, 100]  # 分批获利阈值
}

# 自定义消息模板
MESSAGE_TEMPLATES = {
    "buy_signal": "📉 {symbol} 买入机会\n💰 价格: ${price:.4f}\n📊 24h: {change:.2f}%\n🛒 建议: 考虑定投",
    "sell_signal": "📈 {symbol} 卖出机会\n💰 价格: ${price:.4f}\n📊 24h: {change:.2f}%\n💸 建议: 考虑获利",
    "major_buy": "🚨 {symbol} 抄底机会！\n💰 价格: ${price:.4f}\n📉 暴跌: {change:.2f}%\n🛒 强烈建议: 加仓买入！",
    "major_sell": "🚀 {symbol} 获利良机！\n💰 价格: ${price:.4f}\n📈 暴涨: {change:.2f}%\n💸 强烈建议: 获利了结！"
}