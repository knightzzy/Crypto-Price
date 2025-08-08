#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def test_cooldown():
    """测试冷却机制"""
    conn = sqlite3.connect('crypto_monitor.db')
    cursor = conn.cursor()
    
    # 查询PENDLE最近1小时的通知
    cursor.execute("""
        SELECT notification_type, timestamp 
        FROM notification_history 
        WHERE symbol = 'PENDLE' AND timestamp > datetime('now', '-1 hours')
        ORDER BY timestamp DESC
    """)
    
    results = cursor.fetchall()
    print(f"PENDLE最近1小时通知数量: {len(results)}")
    
    for i, (ntype, timestamp) in enumerate(results, 1):
        print(f"  {i}. {timestamp} - {ntype}")
    
    # 查询所有PENDLE通知
    cursor.execute("""
        SELECT notification_type, timestamp 
        FROM notification_history 
        WHERE symbol = 'PENDLE'
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    
    all_results = cursor.fetchall()
    print(f"\nPENDLE最近10条通知:")
    
    for i, (ntype, timestamp) in enumerate(all_results, 1):
        print(f"  {i}. {timestamp} - {ntype}")
    
    conn.close()

if __name__ == "__main__":
    test_cooldown()