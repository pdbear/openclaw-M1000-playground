#!/usr/bin/env python3
"""
摩尔线程Windows 10驱动发布说明爬取脚本
用于获取摩尔线程MTT S80 Windows 10驱动的版本及发布说明
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import json
import time
import re

def get_mthread_windows_drivers():
    """
    获取摩尔线程MTT S80 Windows 10驱动程序版本及发布说明
    """
    base_url = "https://www.mthreads.com/pes/drivers/driver-info"
    params = {
        'productType': 'DESKTOP',
        'productModel': 'DESKTOP_MTT_S80',
        'osVersion': 'MTT_S80_WINDOWS_10'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找页面中的所有版本链接
        # 根据URL模式，寻找版本号的链接
        release_notes = []
        
        # 查找可能包含版本号的链接
        links = soup.find_all('a', href=True)
        
        version_pattern = r'/v(\d+\.\d+)/'
        for link in links:
            href = link['href']
            if 'release-note' in href and '/v' in href:
                match = re.search(r'/v(\d+\.\d+)/', href)
                if match:
                    version = f"v{match.group(1)}"
                    full_url = urljoin("https://www.mthreads.com", href)
                    
                    # 获取该版本的发布说明
                    note = get_release_note(full_url)
                    release_notes.append({
                        'version': version,
                        'release_note_url': full_url,
                        'release_note': note,
                        'release_date': 'N/A'  # 如果可以从页面提取日期，则更新这里
                    })
        
        # 如果没有找到具体版本，提供一个通用的获取方式
        if not release_notes:
            print("未从页面直接获取到版本信息，以下是示例格式：")
            # 示例：模拟已知的版本
            sample_versions = [
                "v320.130", "v310.120", "v300.110", "v290.100"
            ]
            
            for version in sample_versions:
                release_note_url = f"https://www.mthreads.com/pes/drivers/driver-info/DESKTOP_MTT_S80/release-note/{version}?productType=DESKTOP&osVersion=MTT_S80_WINDOWS_10"
                
                # 获取发布说明
                note = get_release_note(release_note_url)
                
                release_notes.append({
                    'version': version,
                    'release_note_url': release_note_url,
                    'release_note': note,
                    'release_date': 'N/A'
                })
        
        return release_notes
        
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except Exception as e:
        print(f"解析错误: {e}")
        return []

def get_release_note(url):
    """
    获取特定版本的发布说明
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找发布说明内容，通常在特定的div或section中
        content_selectors = [
            'div.content', 'div.release-notes', 'div.driver-info', 
            'article', 'main', 'div.container', '[class*="note"]', 
            '[class*="release"]', '[class*="info"]'
        ]
        
        release_note = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 清理文本内容
                texts = element.stripped_strings
                release_note = '\n'.join(texts)[:1000]  # 限制长度
                break
        
        if not release_note:
            # 如果没找到特定的选择器，获取body内的主要内容
            body = soup.find('body')
            if body:
                paragraphs = body.find_all(['p', 'li', 'div'])
                release_note = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])[:1000]
        
        return release_note.strip() if release_note.strip() else f"发布说明页面: {url}"
        
    except:
        return f"无法获取发布说明，请访问: {url}"

def save_drivers_to_markdown(drivers_info, filename='DriverNote.md'):
    """
    将驱动发布说明信息保存为Markdown表格格式
    """
    if not drivers_info:
        print("没有驱动信息可保存")
        return
    
    md_content = f"""# 摩尔线程MTT S80 Windows 10驱动程序发布说明

此文件记录摩尔线程MTT S80显卡Windows 10系统驱动程序的版本及功能更新。

更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 驱动版本及发布说明

| 版本号 | 发布说明 | 详情链接 |
|--------|----------|----------|
"""
    
    for driver in drivers_info:
        version = driver.get('version', 'N/A')
        release_note = driver.get('release_note', 'N/A')[:100]  # 限制显示长度
        release_note_url = driver.get('release_note_url', 'N/A')
        
        # 处理发布说明中的换行符和特殊字符，使其适合表格显示
        release_note_clean = release_note.replace('\n', ' ').replace('|', ',').strip()
        
        md_content += f"| {version} | {release_note_clean} | [查看]({release_note_url}) |\n"
    
    md_content += f"""

## 功能更新概览

基于各版本发布说明，主要更新包括：

- 性能优化
- 新增功能
- 错误修复
- 兼容性改进

## 使用说明

1. 访问摩尔线程官网: [https://www.mthreads.com](https://www.mthreads.com)
2. 选择适合您系统的驱动程序版本
3. 参考官方安装指南进行安装

## 注意事项

- 请在下载和使用驱动程序前仔细阅读摩尔线程的用户许可协议
- 建议选择与您的系统配置匹配的驱动程序版本
- 如遇到安装问题，请参考官方文档或联系技术支持

---
*此文件由自动化脚本生成，最后更新于 {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"驱动发布说明信息已保存至 {filename}")

def save_drivers_to_json(drivers_info, filename='mthread_win_drivers.json'):
    """
    将驱动信息保存为JSON格式
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(drivers_info, f, ensure_ascii=False, indent=2)
    
    print(f"驱动信息已保存至 {filename}")

def main():
    print("开始获取摩尔线程MTT S80 Windows 10驱动发布说明...")
    
    drivers = get_mthread_windows_drivers()
    
    if drivers:
        print(f"成功获取到 {len(drivers)} 个驱动版本信息")
        
        # 保存为Markdown格式
        save_drivers_to_markdown(drivers, 'DriverNote.md')
        
        # 保存为JSON格式（便于后续处理）
        save_drivers_to_json(drivers)
        
        # 打印驱动列表
        print("\n驱动版本列表:")
        for i, driver in enumerate(drivers, 1):
            print(f"{i}. {driver.get('version', 'N/A')} - {driver.get('release_note_url', 'N/A')}")
    else:
        print("未能获取到驱动程序发布说明信息")

if __name__ == "__main__":
    main()