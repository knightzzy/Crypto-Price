#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币价格监控系统
监控指定币种价格变动，通过企业微信发送买卖提醒

支持币种：RAY, CRV, PENDLE, CAKE
功能：价格上涨提醒卖出，价格下跌提醒买入
"""

import requests
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# ==================== USER CONFIG ====================
# 企业微信机器人webhook地址
WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=46e4e50e-8aa7-4b2f-8983-41800deafa5f"

# 监控的币种列表
MONITOR_SYMBOLS = ["RAY", "CRV", "PENDLE", "CAKE"]

# 价格变动阈值配置（百分比）
PRICE_THRESHOLDS = {
    "buy_threshold": -5.0,   # 价格下跌5%时提醒买入
    "sell_threshold": 8.0,   # 价格上涨8%时提醒卖出
    "major_drop": -15.0,     # 大幅下跌15%时强烈提醒买入
    "major_rise": 20.0       # 大幅上涨20%时强烈提醒卖出
}

# 监控间隔（秒）
MONITOR_INTERVAL = 300  # 5分钟检查一次

# 同一币种通知冷却时间（秒）
NOTIFY_COOLDOWN = 3600  # 1小时内同一币种同类型通知只发送一次

# API配置
API_BASE_URL = "https://api.coingecko.com/api/v3"
API_TIMEOUT = 10

# ==================== END CONFIG ====================

class CryptoMonitor:
    """加密货币价格监控器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.price_history = {}  # 存储历史价格数据
        self.last_notify_time = {}  # 记录上次通知时间，避免频繁通知
        self.coin_id_mapping = {
            "RAY": "raydium",
            "CRV": "curve-dao-token", 
            "PENDLE": "pendle",
            "CAKE": "pancakeswap-token"
        }
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('crypto_monitor')
        logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler('crypto_monitor.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_crypto_prices(self) -> Optional[Dict[str, float]]:
        """获取加密货币价格数据"""
        try:
            # 构建API请求URL
            coin_ids = ",".join([self.coin_id_mapping[symbol] for symbol in MONITOR_SYMBOLS])
            url = f"{API_BASE_URL}/simple/price"
            params = {
                "ids": coin_ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # 转换为我们需要的格式
            prices = {}
            for symbol in MONITOR_SYMBOLS:
                coin_id = self.coin_id_mapping[symbol]
                if coin_id in data:
                    prices[symbol] = {
                        "price": data[coin_id]["usd"],
                        "change_24h": data[coin_id].get("usd_24h_change", 0)
                    }
            
            return prices
            
        except requests.RequestException as e:
            self.logger.error(f"获取价格数据失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"处理价格数据时出错: {e}")
            return None
    
    def send_wechat_notification(self, message: str) -> bool:
        """发送企业微信通知"""
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(
                WECHAT_WEBHOOK,
                json=payload,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") == 0:
                self.logger.info(f"通知发送成功: {message[:50]}...")
                return True
            else:
                self.logger.error(f"通知发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送通知时出错: {e}")
            return False
    
    def check_price_alerts(self, current_prices: Dict[str, Dict]) -> List[str]:
        """检查价格预警条件"""
        alerts = []
        current_time = time.time()
        
        for symbol, price_data in current_prices.items():
            current_price = price_data["price"]
            change_24h = price_data["change_24h"]
            
            # 检查是否需要通知（避免频繁通知）
            last_notify_key = f"{symbol}_notify"
            if (last_notify_key in self.last_notify_time and 
                current_time - self.last_notify_time[last_notify_key] < NOTIFY_COOLDOWN):
                continue
            
            # 根据24小时涨跌幅判断买卖时机
            alert_message = None
            
            if change_24h <= PRICE_THRESHOLDS["major_drop"]:
                # 大幅下跌，强烈建议买入
                alert_message = (
                    f"🚨 {symbol} 大幅下跌警报！\n"
                    f"💰 当前价格: ${current_price:.4f}\n"
                    f"📉 24h跌幅: {change_24h:.2f}%\n"
                    f"🛒 强烈建议：考虑加仓买入！\n"
                    f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            elif change_24h <= PRICE_THRESHOLDS["buy_threshold"]:
                # 普通下跌，建议买入
                alert_message = (
                    f"📉 {symbol} 价格下跌提醒\n"
                    f"💰 当前价格: ${current_price:.4f}\n"
                    f"📊 24h跌幅: {change_24h:.2f}%\n"
                    f"🛒 建议：可考虑定投买入\n"
                    f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            elif change_24h >= PRICE_THRESHOLDS["major_rise"]:
                # 大幅上涨，强烈建议卖出
                alert_message = (
                    f"🚀 {symbol} 大幅上涨警报！\n"
                    f"💰 当前价格: ${current_price:.4f}\n"
                    f"📈 24h涨幅: {change_24h:.2f}%\n"
                    f"💸 强烈建议：考虑获利了结！\n"
                    f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            elif change_24h >= PRICE_THRESHOLDS["sell_threshold"]:
                # 普通上涨，建议卖出
                alert_message = (
                    f"📈 {symbol} 价格上涨提醒\n"
                    f"💰 当前价格: ${current_price:.4f}\n"
                    f"📊 24h涨幅: {change_24h:.2f}%\n"
                    f"💸 建议：可考虑部分获利\n"
                    f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            if alert_message:
                alerts.append(alert_message)
                self.last_notify_time[last_notify_key] = current_time
        
        return alerts
    
    def run_monitor(self):
        """运行监控主循环"""
        self.logger.info("🚀 加密货币价格监控系统启动")
        self.logger.info(f"📊 监控币种: {', '.join(MONITOR_SYMBOLS)}")
        self.logger.info(f"⏱️ 监控间隔: {MONITOR_INTERVAL}秒")
        
        # 发送启动通知
        startup_message = (
            f"🤖 加密货币监控系统已启动\n"
            f"📊 监控币种: {', '.join(MONITOR_SYMBOLS)}\n"
            f"📉 买入提醒: 下跌{abs(PRICE_THRESHOLDS['buy_threshold'])}%\n"
            f"📈 卖出提醒: 上涨{PRICE_THRESHOLDS['sell_threshold']}%\n"
            f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.send_wechat_notification(startup_message)
        
        while True:
            try:
                # 获取当前价格
                current_prices = self.get_crypto_prices()
                
                if current_prices:
                    # 记录价格信息
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.logger.info(f"[{timestamp}] 价格更新:")
                    for symbol, data in current_prices.items():
                        self.logger.info(
                            f"  {symbol}: ${data['price']:.4f} "
                            f"(24h: {data['change_24h']:+.2f}%)"
                        )
                    
                    # 检查预警条件
                    alerts = self.check_price_alerts(current_prices)
                    
                    # 发送预警通知
                    for alert in alerts:
                        self.send_wechat_notification(alert)
                        time.sleep(1)  # 避免发送过快
                
                else:
                    self.logger.warning("未能获取价格数据，跳过本次检查")
                
                # 等待下次检查
                time.sleep(MONITOR_INTERVAL)
                
            except KeyboardInterrupt:
                self.logger.info("收到停止信号，正在关闭监控系统...")
                break
            except Exception as e:
                self.logger.error(f"监控过程中出现错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续

def main():
    """主函数"""
    monitor = CryptoMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()