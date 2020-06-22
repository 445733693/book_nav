#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

html_template = """
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="css/main.css"/>
<title>%s</title>
</head>
<body>
<h1>%s</h1>
<div>
%s
</div>
</body>
</html>
"""


def parse_books():  # 解析books.json文件，获取分类以及所有书名
    with open('books.json', 'r') as f:
        books = json.load(f)
        return books


def gen_nav_list(books):  # 生成一级目录列表到nav_list.json文件
    with open('nav_list.json', 'w') as nav_file:
        nav_list = []
        for category in books:
            en = category["en"]
            zh = category["zh"]
            file_name = en + '.html'
            item = (file_name, zh)
            nav_list.append(item)
        json.dump(nav_list, nav_file, ensure_ascii=False)  # ensure_ascii=False这样输出的中文就不是/u1241了


def gen_nav(books):  # 生成一级目录html文件
    for category in books:
        en = category["en"]
        zh = category["zh"]
        file_name = en + '.html'
        file_path = 'htmls/' + file_name
        # if os.path.exists(file_path):
        #     continue
        book_html_list = []
        for book in category["books"]:
            pingyin = book[0]
            book_zh = book[1]
            book_tag = '''<p><a href="%s.html">%s</a></p>''' % (pingyin, book_zh)
            book_html_list.append(book_tag)
        content = html_template % (
            zh,
            zh,
            "\n".join(book_html_list)
        )
        with open(file_path, 'w') as f:
            f.write(content)


books = parse_books()
gen_nav_list(books)
gen_nav(books)

for category in books:
    cate_en = category["en"]
    cate_name = cate_en + '.html'
    for book in category["books"]:
        pingyin = book[0]
        zh = book[1]
        file_name = cate_en + '_' + pingyin + '.html'
        file_path = 'htmls/' + file_name
        # if os.path.exists(file_path):
        #     continue
        back_url = '''<p><a href="%s.html">%s</a></p>''' % (cate_name, "返回上一层")
        description = "这是书的简介"
        detail = '''<p>%s</p>''' % description
        content = html_template % (
            zh,
            zh,
            "\n".join([back_url, detail, back_url])
        )
        with open(file_path,'w') as f:
            f.write(content)
