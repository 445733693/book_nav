#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from detail_scraper import DetailScraper
from detail_scraper import BookDetail
from detail_scraper import ShortComment
from detail_scraper import Comment
from log import logger

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

detail_scraper = DetailScraper()


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
    logger.info("开始生成目录html")
    for category in books:
        en = category["en"]
        zh = category["zh"]
        file_name = en + '.html'
        file_path = 'htmls/' + file_name
        # if os.path.exists(file_path):
        #     continue
        book_html_list = []
        for i, book in enumerate(category["books"]):
            pingyin = book[0]
            book_zh = book[1]
            book_tag = '''<p><a href="%s.html">%d.%s</a></p>''' % (en + '_' + pingyin, i + 1, book_zh)
            book_html_list.append(book_tag)
        content = html_template % (
            zh,
            zh,
            "\n".join(book_html_list)
        )
        with open(file_path, 'w') as f:
            f.write(content)
        logger.info("生成目录：%s", zh)


def gen_book_detail_html(books):  # 生成每本书的详情html文件
    logger.info("开始生成书本详情html")
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
            back_url = '''<p><a href="%s">%s</a></p>''' % (cate_name, "返回上一层")
            book_detail = gen_book_detail(zh)
            content = html_template % (
                zh,
                zh,
                "\n".join([back_url, book_detail, back_url])
            )
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info("完成书籍详情：%s",category["zh"]+': '+zh)

def gen_book_detail(book_name):
    logger.info("开始爬取书籍详情：%s",book_name)
    book_detail = detail_scraper.get_detail(book_name)
    content = []
    title = '''<h3>%s</h3>''' % book_detail.title
    content.append(title)
    intro = '''<h4>内容简介</h4>\n<p>%s</p>''' % book_detail.intro
    content.append(intro)
    author = '''<h4>作者简介</h4>\n<p>%s</p>''' % book_detail.author
    content.append(author)
    content.append('''<h4>短评</h4>''')
    for short_comment in book_detail.short_comments:
        sc = '''<hr/><p>用户：%s；有用：%s</p>\n<p>%s</p>\n<p></p>''' % (
        short_comment.name, short_comment.vote_count, short_comment.content)
        content.append(sc)
    content.append('''<h4>书评</h4>''')
    for comment in book_detail.comments:
        c = '''<hr/><p>用户：%s；有用：%s；没用：%s</p>\n<p>标题：%s</p>\n<p>%s</p>\n<p></p>''' % (
            comment.name, comment.up_vote_count, comment.down_vote_count, comment.small_title, comment.content)
        content.append(c)
    logger.info("完成爬取书籍详情：%s", book_name)
    return '\n'.join(content)


books = parse_books()
gen_nav_list(books)
gen_nav(books)
gen_book_detail_html(books)
