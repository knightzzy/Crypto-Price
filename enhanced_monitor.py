#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版加密货币价格监控系统
支持配置文件、数据持久化、异常检测等高级功能
"""

import requests
import time
import json
import logging
import sqlite3
import os
import importlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from logging.handlers import RotatingFileHandler

# 导入配置
try:
    import config
    from config import *
except ImportError:
    # 如果没有配置文件，使用默认配置
    print("警告: 未找到config.py，使用默认配置")
    import crypto_monitor as config
    from crypto_monitor import *

class EnhancedCryptoMonitor:
    """增强版加密货币价格监控器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db_path = "crypto_monitor.db"
        self._init_database()
        self.notification_count = 0
        self.daily_notification_count = 0
        self.last_reset_date = datetime.now().date()
        
        # 配置文件监控
        self.config_file_path = "config.py"
        self.last_config_mtime = self._get_config_mtime()
        self.current_symbols = list(MONITOR_SYMBOLS)  # 保存当前监控的币种
        
    def _get_config_mtime(self) -> float:
        """获取配置文件的修改时间"""
        try:
            if os.path.exists(self.config_file_path):
                return os.path.getmtime(self.config_file_path)
        except Exception:
            pass
        return 0
    
    def _reload_config(self) -> bool:
        """重新加载配置文件"""
        try:
            # 重新导入配置模块
            importlib.reload(config)
            
            # 更新全局变量
            global MONITOR_SYMBOLS, PRICE_THRESHOLDS, MONITOR_INTERVAL
            global WEBHOOK_URL, RISK_MANAGEMENT, LOG_CONFIG
            
            from config import (
                MONITOR_SYMBOLS, PRICE_THRESHOLDS, MONITOR_INTERVAL,
                WEBHOOK_URL, RISK_MANAGEMENT, LOG_CONFIG
            )
            
            self.logger.info(f"🔄 配置已重新加载")
            self.logger.info(f"📊 新的监控币种: {', '.join(MONITOR_SYMBOLS)}")
            
            # 检查币种是否有变化
            if set(MONITOR_SYMBOLS) != set(self.current_symbols):
                added_symbols = set(MONITOR_SYMBOLS) - set(self.current_symbols)
                removed_symbols = set(self.current_symbols) - set(MONITOR_SYMBOLS)
                
                change_msg = "📝 监控币种更新:\n"
                if added_symbols:
                    change_msg += f"➕ 新增: {', '.join(added_symbols)}\n"
                if removed_symbols:
                    change_msg += f"➖ 移除: {', '.join(removed_symbols)}\n"
                change_msg += f"📊 当前监控: {', '.join(MONITOR_SYMBOLS)}"
                
                self.send_enhanced_notification(change_msg)
                self.current_symbols = list(MONITOR_SYMBOLS)
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置重新加载失败: {e}")
            return False
    
    def _check_config_changes(self) -> bool:
        """检查配置文件是否有变化"""
        current_mtime = self._get_config_mtime()
        if current_mtime > self.last_config_mtime:
            self.last_config_mtime = current_mtime
            return self._reload_config()
        return False
    
    def _setup_logger(self) -> logging.Logger:
        """设置增强的日志记录器"""
        logger = logging.getLogger('enhanced_crypto_monitor')
        logger.setLevel(getattr(logging, LOG_CONFIG.get('level', 'INFO')))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 创建轮转文件处理器
        file_handler = RotatingFileHandler(
            LOG_CONFIG.get('file_name', 'crypto_monitor.log'),
            maxBytes=LOG_CONFIG.get('max_file_size', 10*1024*1024),
            backupCount=LOG_CONFIG.get('backup_count', 5),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(LOG_CONFIG.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _init_database(self):
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建价格历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建通知历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    price REAL NOT NULL,
                    change_24h REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitor_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("数据库初始化完成")
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
    
    def save_price_data(self, symbol: str, price_data: Dict):
        """保存价格数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_history (symbol, price, change_24h, volume_24h, market_cap)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                symbol,
                price_data.get('price', 0),
                price_data.get('change_24h', 0),
                price_data.get('volume_24h', 0),
                price_data.get('market_cap', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"保存价格数据失败: {e}")
    
    def save_notification(self, symbol: str, notification_type: str, message: str, price: float, change_24h: float):
        """保存通知记录到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notification_history (symbol, notification_type, message, price, change_24h)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, notification_type, message, price, change_24h))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"保存通知记录失败: {e}")
    
    def get_recent_notifications(self, symbol: str, hours: int = 1) -> List[Dict]:
        """获取最近的通知记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            cursor.execute('''
                SELECT notification_type, timestamp FROM notification_history
                WHERE symbol = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (symbol, since_time))
            
            results = cursor.fetchall()
            conn.close()
            
            return [{'type': row[0], 'timestamp': row[1]} for row in results]
            
        except Exception as e:
            self.logger.error(f"获取通知记录失败: {e}")
            return []
    
    def get_enhanced_crypto_prices(self) -> Optional[Dict[str, Dict]]:
        """获取增强的加密货币价格数据"""
        try:
            # 构建API请求URL
            coin_ids = ",".join([COIN_ID_MAPPING[symbol] for symbol in MONITOR_SYMBOLS if symbol in COIN_ID_MAPPING])
            url = f"{API_CONFIG['base_url']}/simple/price"
            params = {
                "ids": coin_ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
            
            # 重试机制
            for attempt in range(API_CONFIG.get('retry_times', 3)):
                try:
                    response = requests.get(url, params=params, timeout=API_CONFIG.get('timeout', 10))
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == API_CONFIG.get('retry_times', 3) - 1:
                        raise e
                    time.sleep(API_CONFIG.get('retry_delay', 5))
            
            data = response.json()
            
            # 转换为我们需要的格式
            prices = {}
            for symbol in MONITOR_SYMBOLS:
                if symbol in COIN_ID_MAPPING:
                    coin_id = COIN_ID_MAPPING[symbol]
                    if coin_id in data:
                        price_info = {
                            "price": data[coin_id]["usd"],
                            "change_24h": data[coin_id].get("usd_24h_change", 0),
                            "volume_24h": data[coin_id].get("usd_24h_vol", 0),
                            "market_cap": data[coin_id].get("usd_market_cap", 0)
                        }
                        prices[symbol] = price_info
                        
                        # 保存到数据库
                        self.save_price_data(symbol, price_info)
            
            return prices
            
        except requests.RequestException as e:
            self.logger.error(f"获取价格数据失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"处理价格数据时出错: {e}")
            return None
    
    def detect_anomalies(self, symbol: str, current_data: Dict) -> List[str]:
        """检测价格异常"""
        anomalies = []
        
        if not ANOMALY_DETECTION.get('enable', False):
            return anomalies
        
        try:
            # 检测价格异常波动
            change_24h = abs(current_data.get('change_24h', 0))
            if change_24h > ANOMALY_DETECTION.get('price_spike_threshold', 50):
                anomalies.append(f"{symbol} 价格异常波动: {change_24h:.2f}%")
            
            # 检测成交量异常
            # 这里需要历史数据对比，简化处理
            volume_24h = current_data.get('volume_24h', 0)
            if volume_24h > 0:  # 如果有成交量数据
                # 可以添加更复杂的成交量异常检测逻辑
                pass
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
        
        return anomalies
    
    def format_notification_message(self, template_key: str, symbol: str, price_data: Dict) -> str:
        """格式化通知消息"""
        try:
            template = MESSAGE_TEMPLATES.get(template_key, "")
            if not template:
                return f"{symbol} 价格提醒: ${price_data['price']:.4f}"
            
            return template.format(
                symbol=symbol,
                price=price_data['price'],
                change=price_data['change_24h'],
                volume=price_data.get('volume_24h', 0),
                market_cap=price_data.get('market_cap', 0)
            ) + f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        except Exception as e:
            self.logger.error(f"格式化消息失败: {e}")
            return f"{symbol} 价格提醒: ${price_data['price']:.4f}"
    
    def send_enhanced_notification(self, message: str) -> bool:
        """发送增强的企业微信通知"""
        # 检查每日通知限制
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_notification_count = 0
            self.last_reset_date = current_date
        
        if self.daily_notification_count >= RISK_MANAGEMENT.get('max_daily_notifications', 20):
            self.logger.warning("已达到每日最大通知数量限制")
            return False
        
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
                timeout=API_CONFIG.get('timeout', 10)
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") == 0:
                self.daily_notification_count += 1
                self.logger.info(f"通知发送成功 ({self.daily_notification_count}/{RISK_MANAGEMENT.get('max_daily_notifications', 20)}): {message[:50]}...")
                return True
            else:
                self.logger.error(f"通知发送失败: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送通知时出错: {e}")
            return False
    
    def check_enhanced_alerts(self, current_prices: Dict[str, Dict]) -> List[Tuple[str, str, str]]:
        """检查增强的价格预警条件"""
        alerts = []  # (symbol, message_type, message)
        
        for symbol, price_data in current_prices.items():
            current_price = price_data["price"]
            change_24h = price_data["change_24h"]
            
            # 检查最近通知历史，避免频繁通知
            recent_notifications = self.get_recent_notifications(symbol, hours=NOTIFY_COOLDOWN//3600)
            
            # 检测异常
            anomalies = self.detect_anomalies(symbol, price_data)
            for anomaly in anomalies:
                self.logger.warning(anomaly)
            
            # 紧急止损检测
            emergency_threshold = RISK_MANAGEMENT.get('emergency_stop_loss', -30)
            if change_24h <= emergency_threshold:
                message = f"🆘 {symbol} 紧急止损警报！\n💰 价格: ${current_price:.4f}\n📉 暴跌: {change_24h:.2f}%\n⚠️ 建议: 立即止损！"
                alerts.append((symbol, "emergency_stop", message))
                continue
            
            # 检查是否在冷却期内
            if any(notif['type'] in ['buy', 'sell', 'major_buy', 'major_sell'] 
                   for notif in recent_notifications):
                continue
            
            # 分级预警检测
            alert_type = None
            if change_24h <= PRICE_THRESHOLDS["major_buy"]:
                alert_type = "major_buy"
            elif change_24h <= PRICE_THRESHOLDS["buy_threshold"]:
                alert_type = "buy_signal"
            elif change_24h >= PRICE_THRESHOLDS["major_sell"]:
                alert_type = "major_sell"
            elif change_24h >= PRICE_THRESHOLDS["sell_threshold"]:
                alert_type = "sell_signal"
            
            if alert_type:
                message = self.format_notification_message(alert_type, symbol, price_data)
                alerts.append((symbol, alert_type, message))
        
        return alerts
    
    def run_enhanced_monitor(self):
        """运行增强版监控主循环"""
        self.logger.info("🚀 增强版加密货币价格监控系统启动")
        self.logger.info(f"📊 监控币种: {', '.join(MONITOR_SYMBOLS)}")
        self.logger.info(f"⏱️ 监控间隔: {MONITOR_INTERVAL}秒")
        self.logger.info(f"🗄️ 数据库: {self.db_path}")
        
        # 发送启动通知
        startup_message = (
            f"🤖 增强版加密货币监控系统已启动\n"
            f"📊 监控币种: {', '.join(MONITOR_SYMBOLS)}\n"
            f"📉 买入阈值: {abs(PRICE_THRESHOLDS['buy_threshold'])}% / {abs(PRICE_THRESHOLDS['major_buy'])}%\n"
            f"📈 卖出阈值: {PRICE_THRESHOLDS['sell_threshold']}% / {PRICE_THRESHOLDS['major_sell']}%\n"
            f"🔔 每日通知限制: {RISK_MANAGEMENT.get('max_daily_notifications', 20)}条\n"
            f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.send_enhanced_notification(startup_message)
        
        while True:
            try:
                # 检查配置文件是否有变化
                self._check_config_changes()
                
                # 获取当前价格
                current_prices = self.get_enhanced_crypto_prices()
                
                if current_prices:
                    # 记录价格信息
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.logger.info(f"[{timestamp}] 价格更新:")
                    for symbol, data in current_prices.items():
                        self.logger.info(
                            f"  {symbol}: ${data['price']:.4f} "
                            f"(24h: {data['change_24h']:+.2f}%) "
                            f"Vol: ${data.get('volume_24h', 0):,.0f}"
                        )
                    
                    # 检查预警条件
                    alerts = self.check_enhanced_alerts(current_prices)
                    
                    # 发送预警通知
                    for symbol, alert_type, message in alerts:
                        if self.send_enhanced_notification(message):
                            # 保存通知记录
                            price_data = current_prices[symbol]
                            self.save_notification(
                                symbol, alert_type, message, 
                                price_data['price'], price_data['change_24h']
                            )
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
    monitor = EnhancedCryptoMonitor()
    monitor.run_enhanced_monitor()

if __name__ == "__main__":
    main()