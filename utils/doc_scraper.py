#!/usr/bin/env python3
"""
摩尔线程文档中心爬虫脚本
用于抓取文档页面并生成表格格式的TechDoc.md文件
"""

import re
import json
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


def get_docs_page():
    """获取摩尔线程文档中心主页面"""
    url = "https://docs.mthreads.com/"
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text


def parse_docs_content(html_content):
    """解析文档页面内容，提取文档信息"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找文档列表区域
    docs_data = []
    
    # 找到所有推荐项
    recommend_items = soup.find_all('div', class_='recommendItem_qnDR')
    
    for item in recommend_items:
        # 获取类别标题
        category_title = ""
        category_header = item.find('div', class_='recommendTitle_VczU')
        if category_header:
            category_title = category_header.get_text(strip=True)
        
        # 获取子文档列表
        sub_contents = item.find_all('a', class_='subContent_lSoW')
        
        for sub_content in sub_contents:
            doc_url = sub_content.get('href')
            if doc_url and not doc_url.startswith('#'):
                # 构建完整URL
                full_url = urljoin('https://docs.mthreads.com/', doc_url)
                
                # 提取文档标题和简介
                doc_title_elem = sub_content.find('div', class_='docTitle_FsZJ')
                doc_subtitle_elem = sub_content.find('div', class_='subDocTitle_aEq3')
                
                doc_title = doc_title_elem.get_text(strip=True) if doc_title_elem else "未知标题"
                doc_subtitle = doc_subtitle_elem.get_text(strip=True) if doc_subtitle_elem else "暂无简介"
                
                docs_data.append({
                    'category': category_title,
                    'title': doc_title,
                    'description': doc_subtitle,
                    'url': full_url
                })
    
    # 同时查找左侧导航树中的文档
    tree_items = soup.find_all('div', role='treeitem')
    for item in tree_items:
        text_elem = item.find(class_='leafText_DmHv')
        if text_elem:
            category_title = text_elem.get_text(strip=True)
            # 这些是分类，可能还有更多链接在页面其他地方
    
    return docs_data


def generate_tech_doc_md(docs_data):
    """生成TechDoc.md内容"""
    md_content = "# 摩尔线程开发文档汇总\n\n"
    md_content += "本文档汇总了摩尔线程开发文档中心的所有文档资源，方便查阅。\n\n"
    
    # 按类别组织
    categories = {}
    for doc in docs_data:
        category = doc['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(doc)
    
    # 添加表格
    md_content += "## 文档总览表\n\n"
    md_content += "| 文档标题 | 文档简介 | 具体链接 |\n"
    md_content += "|---------|----------|----------|\n"
    
    for category in sorted(categories.keys()):
        if category:  # 只处理非空类别
            for doc in categories[category]:
                title = doc['title'].replace('|', '｜')  # 防止破坏表格
                description = doc['description'].replace('|', '｜')
                url = doc['url']
                md_content += f"| {title} | {description} | [{url}]({url}) |\n"
    
    # 添加按类别分组的详细信息
    md_content += "\n## 按类别分组\n\n"
    for category in sorted(categories.keys()):
        if category:
            md_content += f"### {category}\n\n"
            md_content += "| 文档标题 | 文档简介 | 链接 |\n"
            md_content += "|---------|----------|------|\n"
            
            for doc in categories[category]:
                title = doc['title'].replace('|', '｜')
                description = doc['description'].replace('|', '｜')
                url = doc['url']
                md_content += f"| {title} | {description} | [{doc['title']}]({url}) |\n"
            md_content += "\n"
    
    return md_content


def main():
    print("开始抓取摩尔线程文档中心内容...")
    
    # 获取页面内容
    html_content = get_docs_page()
    
    # 解析文档信息
    docs_data = parse_docs_content(html_content)
    
    print(f"共找到 {len(docs_data)} 个文档链接")
    
    # 生成Markdown文档
    tech_doc_content = generate_tech_doc_md(docs_data)
    
    # 保存到TechDoc.md
    with open('TechDoc.md', 'w', encoding='utf-8') as f:
        f.write(tech_doc_content)
    
    print("TechDoc.md 文件已生成完成！")
    
    # 保存原始数据以便后续使用
    with open('tech_docs_data.json', 'w', encoding='utf-8') as f:
        json.dump(docs_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()