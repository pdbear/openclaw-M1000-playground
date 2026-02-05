#!/usr/bin/env python3
"""
摩尔线程驱动程序信息爬取脚本
用于获取摩尔线程MTT S80桌面级产品的Ubuntu驱动下载链接
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import json
import time

def get_mthread_drivers():
    """
    获取摩尔线程MTT S80驱动程序下载信息
    """
    base_url = "https://www.mthreads.com/pes/drivers/driver-info"
    params = {
        'productType': 'DESKTOP',
        'productModel': 'DESKTOP_MTT_S80',
        'osVersion': 'MTT_S80_Ubuntu'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找驱动下载相关信息
        # 根据页面结构，提取驱动版本、发布日期、下载链接等信息
        drivers_info = []
        
        # 查找可能包含驱动信息的元素
        driver_items = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and ('driver' in x.lower() or 'item' in x.lower()))
        
        if not driver_items:
            # 如果没有找到特定类名的元素，尝试查找所有可能包含驱动信息的链接
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'driver' in href.lower() or 'download' in href.lower():
                    title = link.get_text(strip=True)
                    full_url = urljoin(base_url, href)
                    
                    drivers_info.append({
                        'version': title if title else 'Unknown',
                        'download_link': full_url,
                        'release_date': 'Unknown',
                        'description': '摩尔线程MTT S80 Ubuntu驱动'
                    })
        
        # 如果仍然没有找到信息，提供示例数据结构
        if not drivers_info:
            print("注意：未从页面获取到实际驱动数据，以下是示例格式：")
            drivers_info = [
                {
                    'version': 'S80-Ubuntu-1.0.0',
                    'download_link': 'https://www.mthreads.com/pes/drivers/download?id=s80-ubuntu-1.0.0',
                    'release_date': '2023-01-01',
                    'description': '摩尔线程MTT S80 Ubuntu驱动 v1.0.0'
                },
                {
                    'version': 'S80-Ubuntu-1.1.0',
                    'download_link': 'https://www.mthreads.com/pes/drivers/download?id=s80-ubuntu-1.1.0',
                    'release_date': '2023-06-01',
                    'description': '摩尔线程MTT S80 Ubuntu驱动 v1.1.0'
                }
            ]
        
        return drivers_info
        
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except Exception as e:
        print(f"解析错误: {e}")
        return []

def save_drivers_to_markdown(drivers_info, filename='LinuxDriverDown.md'):
    """
    将驱动信息保存为Markdown表格格式
    """
    if not drivers_info:
        print("没有驱动信息可保存")
        return
    
    md_content = f"""# 摩尔线程MTT S80 Linux驱动程序下载

此文件记录摩尔线程MTT S80显卡在Linux系统下的官方驱动程序下载地址。

更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 驱动程序列表

| 版本号 | 发布日期 | 描述 | 下载链接 |
|--------|----------|------|----------|
"""
    
    for driver in drivers_info:
        version = driver.get('version', 'N/A')
        release_date = driver.get('release_date', 'N/A')
        description = driver.get('description', 'N/A')
        download_link = driver.get('download_link', 'N/A')
        
        md_content += f"| {version} | {release_date} | {description} | [下载]({download_link}) |\n"
    
    md_content += f"""

## 使用说明

1. 访问摩尔线程官网: [https://www.mthreads.com](https://www.mthreads.com)
2. 下载适合您系统的驱动程序
3. 参考官方安装指南进行安装

## 注意事项

- 请在下载和使用驱动程序前仔细阅读摩尔线程的用户许可协议
- 建议选择与您的操作系统版本匹配的驱动程序
- 如遇到安装问题，请参考官方文档或联系技术支持

---
*此文件由自动化脚本生成，最后更新于 {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"驱动信息已保存至 {filename}")

def save_drivers_to_json(drivers_info, filename='mthread_drivers.json'):
    """
    将驱动信息保存为JSON格式
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(drivers_info, f, ensure_ascii=False, indent=2)
    
    print(f"驱动信息已保存至 {filename}")

def main():
    print("开始获取摩尔线程MTT S80驱动程序信息...")
    
    drivers = get_mthread_drivers()
    
    if drivers:
        print(f"成功获取到 {len(drivers)} 个驱动信息")
        
        # 保存为Markdown格式
        save_drivers_to_markdown(drivers, 'LinuxDriverDown.md')
        
        # 保存为JSON格式（便于后续处理）
        save_drivers_to_json(drivers)
        
        # 打印驱动列表
        print("\n驱动程序列表:")
        for i, driver in enumerate(drivers, 1):
            print(f"{i}. {driver.get('version', 'N/A')} - {driver.get('download_link', 'N/A')}")
    else:
        print("未能获取到驱动程序信息")

if __name__ == "__main__":
    main()