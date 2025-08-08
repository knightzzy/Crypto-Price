#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币监控系统Web仪表板
提供实时价格展示和监控状态查看
"""

import sqlite3
import json
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
from config import MONITOR_SYMBOLS

class DashboardHandler(BaseHTTPRequestHandler):
    """Web仪表板请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/api/prices':
            self.serve_prices_api()
        elif parsed_path.path == '/api/notifications':
            self.serve_notifications_api()
        elif parsed_path.path == '/api/status':
            self.serve_status_api()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """提供仪表板HTML页面"""
        html_content = self.get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_prices_api(self):
        """提供价格数据API"""
        try:
            conn = sqlite3.connect('crypto_monitor.db')
            cursor = conn.cursor()
            
            # 获取最新价格数据
            cursor.execute('''
                SELECT symbol, price, change_24h, volume_24h, timestamp
                FROM price_history
                WHERE timestamp > datetime('now', '-1 hour')
                ORDER BY timestamp DESC
                LIMIT 20
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            # 转换为JSON格式
            prices = []
            for row in results:
                prices.append({
                    'symbol': row[0],
                    'price': row[1],
                    'change_24h': row[2],
                    'volume_24h': row[3],
                    'timestamp': row[4]
                })
            
            self.send_json_response(prices)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def serve_notifications_api(self):
        """提供通知历史API"""
        try:
            conn = sqlite3.connect('crypto_monitor.db')
            cursor = conn.cursor()
            
            # 获取最近24小时的通知
            cursor.execute('''
                SELECT symbol, notification_type, message, price, change_24h, timestamp
                FROM notification_history
                WHERE timestamp > datetime('now', '-1 day')
                ORDER BY timestamp DESC
                LIMIT 50
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            # 转换为JSON格式
            notifications = []
            for row in results:
                notifications.append({
                    'symbol': row[0],
                    'type': row[1],
                    'message': row[2],
                    'price': row[3],
                    'change_24h': row[4],
                    'timestamp': row[5]
                })
            
            self.send_json_response(notifications)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def serve_status_api(self):
        """提供系统状态API"""
        try:
            import os
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'database_size': os.path.getsize('crypto_monitor.db') if os.path.exists('crypto_monitor.db') else 0,
                'log_size': os.path.getsize('crypto_monitor.log') if os.path.exists('crypto_monitor.log') else 0,
                'uptime': 'Running',
                'monitored_symbols': MONITOR_SYMBOLS
            }
            
            self.send_json_response(status)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def get_dashboard_html(self):
        """生成仪表板HTML"""
        symbols_str = ', '.join(MONITOR_SYMBOLS)
        symbols_js = str(list(MONITOR_SYMBOLS))
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 加密货币监控仪表板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .price-card {
            text-align: center;
        }
        
        .symbol {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .price {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .change {
            font-size: 1.2em;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 20px;
        }
        
        .change.positive {
            background: #d4edda;
            color: #155724;
        }
        
        .change.negative {
            background: #f8d7da;
            color: #721c24;
        }
        
        .volume {
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }
        
        .notifications {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .notification-item {
            border-left: 4px solid #007bff;
            padding: 10px 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }
        
        .notification-item.buy {
            border-left-color: #28a745;
        }
        
        .notification-item.sell {
            border-left-color: #dc3545;
        }
        
        .notification-time {
            font-size: 0.8em;
            color: #666;
            float: right;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #0056b3;
        }
        
        @media (max-width: 768px) {
            .status-bar {
                flex-direction: column;
                gap: 10px;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 加密货币监控仪表板</h1>
            <p>实时监控 %(symbols_str)s 价格变动</p>
        </div>
        
        <div class="status-bar">
            <div>
                <strong>🟢 系统状态:</strong> <span id="system-status">运行中</span>
            </div>
            <div>
                <strong>⏰ 最后更新:</strong> <span id="last-update">--</span>
            </div>
            <div>
                <button class="refresh-btn" onclick="refreshData()">🔄 刷新数据</button>
            </div>
        </div>
        
        <div class="grid" id="price-grid">
            <div class="loading">📊 正在加载价格数据...</div>
        </div>
        
        <div class="notifications">
            <h3>📢 最近通知</h3>
            <div id="notifications-list">
                <div class="loading">📱 正在加载通知历史...</div>
            </div>
        </div>
    </div>
    
    <script>
        // 全局变量
        let refreshInterval;
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            // 每30秒自动刷新
            refreshInterval = setInterval(refreshData, 30000);
        });
        
        // 刷新数据
        function refreshData() {
            loadPrices();
            loadNotifications();
            updateLastUpdateTime();
        }
        
        // 加载价格数据
        async function loadPrices() {
            try {
                const response = await fetch('/api/prices');
                const prices = await response.json();
                
                if (prices.error) {
                    throw new Error(prices.error);
                }
                
                displayPrices(prices);
            } catch (error) {
                console.error('加载价格数据失败:', error);
                document.getElementById('price-grid').innerHTML = 
                    '<div class="loading">❌ 加载价格数据失败</div>';
            }
        }
        
        // 显示价格数据
        function displayPrices(prices) {
            const symbols = %(symbols_js)s;
            const latestPrices = {};
            
            // 获取每个币种的最新价格
            prices.forEach(price => {
                if (!latestPrices[price.symbol] || 
                    new Date(price.timestamp) > new Date(latestPrices[price.symbol].timestamp)) {
                    latestPrices[price.symbol] = price;
                }
            });
            
            const grid = document.getElementById('price-grid');
            grid.innerHTML = '';
            
            symbols.forEach(symbol => {
                const priceData = latestPrices[symbol];
                if (priceData) {
                    const card = createPriceCard(priceData);
                    grid.appendChild(card);
                }
            });
        }
        
        // 创建价格卡片
        function createPriceCard(priceData) {
            const card = document.createElement('div');
            card.className = 'card price-card';
            
            const changeClass = priceData.change_24h >= 0 ? 'positive' : 'negative';
            const changeSymbol = priceData.change_24h >= 0 ? '+' : '';
            
            card.innerHTML = `
                <div class="symbol">${priceData.symbol}</div>
                <div class="price">${priceData.price.toFixed(4)}</div>
                <div class="change ${changeClass}">
                    ${changeSymbol}${priceData.change_24h.toFixed(2)}%%
                </div>
                <div class="volume">
                    24h成交量: ${formatNumber(priceData.volume_24h)}
                </div>
            `;
            
            return card;
        }
        
        // 加载通知历史
        async function loadNotifications() {
            try {
                const response = await fetch('/api/notifications');
                const notifications = await response.json();
                
                if (notifications.error) {
                    throw new Error(notifications.error);
                }
                
                displayNotifications(notifications);
            } catch (error) {
                console.error('加载通知历史失败:', error);
                document.getElementById('notifications-list').innerHTML = 
                    '<div class="loading">❌ 加载通知历史失败</div>';
            }
        }
        
        // 显示通知历史
        function displayNotifications(notifications) {
            const container = document.getElementById('notifications-list');
            
            if (notifications.length === 0) {
                container.innerHTML = '<div class="loading">📭 暂无通知记录</div>';
                return;
            }
            
            container.innerHTML = '';
            
            notifications.slice(0, 10).forEach(notification => {
                const item = document.createElement('div');
                item.className = `notification-item ${getNotificationType(notification.type)}`;
                
                const time = new Date(notification.timestamp).toLocaleString('zh-CN');
                
                item.innerHTML = `
                    <div class="notification-time">${time}</div>
                    <strong>${notification.symbol}</strong> - ${getNotificationTypeText(notification.type)}<br>
                    <small>价格: ${notification.price.toFixed(4)} | 变动: ${notification.change_24h.toFixed(2)}%%</small>
                `;
                
                container.appendChild(item);
            });
        }
        
        // 获取通知类型样式
        function getNotificationType(type) {
            if (type.includes('buy')) return 'buy';
            if (type.includes('sell')) return 'sell';
            return '';
        }
        
        // 获取通知类型文本
        function getNotificationTypeText(type) {
            const typeMap = {
                'buy_signal': '买入信号',
                'sell_signal': '卖出信号',
                'major_buy': '强烈买入',
                'major_sell': '强烈卖出',
                'emergency_stop': '紧急止损'
            };
            return typeMap[type] || type;
        }
        
        // 格式化数字
        function formatNumber(num) {
            if (num >= 1e9) {
                return (num / 1e9).toFixed(1) + 'B';
            } else if (num >= 1e6) {
                return (num / 1e6).toFixed(1) + 'M';
            } else if (num >= 1e3) {
                return (num / 1e3).toFixed(1) + 'K';
            }
            return num.toFixed(0);
        }
        
        // 更新最后更新时间
        function updateLastUpdateTime() {
            const now = new Date();
            document.getElementById('last-update').textContent = 
                now.toLocaleString('zh-CN');
        }
    </script>
</body>
</html>
        ''' % {'symbols_str': symbols_str, 'symbols_js': symbols_js}

def start_web_server(port=8080):
    """启动Web服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"🌐 Web仪表板启动成功: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Web服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("端口号必须是数字")
            sys.exit(1)
    
    start_web_server(port)