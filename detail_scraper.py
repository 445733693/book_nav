#!/usr/bin/python
# encoding=utf-8


import requests
import time
import json
from log import logger
import os
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from contextlib import closing


class ShortComment:
    def __init__(self, name, vote_count, content):
        self.name = name
        self.vote_count = vote_count
        self.content = content


class Comment:
    def __init__(self, name, small_title, content, up_vote_count, down_vote_count):
        self.name = name
        self.small_title = small_title
        self.content = content
        self.up_vote_count = up_vote_count
        self.down_vote_count = down_vote_count


class BookDetail:
    title = ''
    score = ''
    intro = ''
    author = ''
    short_comments = []
    comments = []

    def __init__(self, title, score, intro, author):
        self.title = title
        self.score = score
        self.intro = intro
        self.author = author

    def add_short_comment(self, short_comment):
        self.short_comments.append(short_comment)

    def add_comment(self, comment):
        self.comments.append(comment)


class DetailScraper:
    home_page = 'https://book.douban.com/'

    def __init__(self):
        logger.info("==============DetailScraper 开始初始化==============")
        opts = Options()
        opts.headless = True
        self.browser = Firefox(options=opts)
        self.browser.get(self.home_page)
        logger.info("==============DetailScraper 初始化完毕==============")

    def get_detail(self, book_name):
        # 搜索
        search = self.browser.find_element_by_id('inp-query')
        search.send_keys(str(book_name).strip())
        search_button = self.browser.find_element_by_class_name('inp-btn')
        search_button.submit()
        time.sleep(3)
        # 获取标题（书名）
        items = self.browser.find_elements_by_class_name('sc-bZQynM')
        a = items[0].find_element_by_class_name('title-text')
        title = a.text
        # 获取详情链接
        detail_url = a.get_attribute('href')
        self.browser.get(detail_url)
        # 获取豆瓣评分
        score = self.browser.find_element_by_class_name('rating_num').text
        # 获取书籍简介、作者简介
        intros = self.browser.find_elements_by_class_name('intro')
        intro = intros[0].text
        intros = intros[1:]
        author = ''
        for x in intros:
            if str(x.text).strip():
                author += '\n' + x.text
        book_detail = BookDetail(title, score, intro, author)
        # 获取短评
        cmt = self.browser.find_element_by_id('comments')
        comments = cmt.find_elements_by_class_name('comment')
        for comment in comments:
            vote_count = comment.find_element_by_class_name('vote-count').text
            name = comment.find_element_by_class_name('comment-info').find_element_by_tag_name('a').text
            content = comment.find_element_by_class_name('comment-content').text
            book_detail.add_short_comment(
                ShortComment(name, vote_count, content)
            )
        # 获取书评
        reviews = self.browser.find_elements_by_css_selector('.main.review-item')
        for review in reviews:
            name = review.find_element_by_class_name('name').text
            small_title = review.find_element_by_tag_name('h2').find_element_by_tag_name('a').text
            content = review.find_element_by_class_name('short-content').text
            up_vote_count = review.find_element_by_css_selector('.action-btn.up').find_element_by_tag_name('span').text
            down_vote_count = review.find_element_by_css_selector('.action-btn.down').find_element_by_tag_name(
                'span').text
            book_detail.add_comment(
                Comment(name, small_title, content, up_vote_count, down_vote_count)
            )
        return book_detail

    def close(self):
        self.browser.close()