#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import json
from gen_html import parse_books
from log import logger

logger.info("开始打包电子书")

title = '书籍导航'
creator = '陈财建'
description = '用来做导航，将书籍分类，并为每本书做了简介，简介来自豆瓣'

nav_file = open('nav_list.json','r')
nav_list = json.load(nav_file)

nav_file.close()

os.mkdir('tmp')

tmpfile = open('tmp/mimetype', 'w')
tmpfile.write('application/epub+zip')
tmpfile.close()

os.mkdir('tmp/META-INF')

tmpfile = open('tmp/META-INF/container.xml', 'w')
tmpfile.write('''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles> <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/> </rootfiles>
</container>
''')
tmpfile.close()

os.mkdir('tmp/OPS')

if os.path.isfile('cover.jpg'):     # 如果有cover.jpg, 用来制作封面
    shutil.copyfile('cover.jpg', 'tmp/OPS/cover.jpg')
    print('Cover.jpg found!')

opfcontent = '''<?xml version="1.0" encoding="UTF-8" ?>
<package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
%(metadata)s
<meta name="cover" content="cover"/>
</metadata>
<manifest>
%(manifest)s
<item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
<item id="cover" href="cover.jpg" media-type="image/jpeg"/>
</manifest>
<spine toc="ncx">
%(ncx)s
</spine>
</package>
'''

dc = '<dc:%(name)s>%(value)s</dc:%(name)s>'
item = "<item id='%(id)s' href='%(url)s' media-type='application/xhtml+xml'/>"
itemref = "<itemref idref='%(id)s'/>"

metadata = '\n'.join([
        dc % {'name': 'title', 'value': title},
        dc % {'name': 'creator', 'value': creator},
        dc % {'name': 'description', 'value': description},
        ])

manifest = []
ncx = []

for htmlitem in nav_list:
    file_name = htmlitem[0]
    zh = htmlitem[1]
    file_path = 'htmls/'+file_name
    content = open(file_path, 'r').read()
    tmpfile = open('tmp/OPS/%s' % file_name, 'w')
    tmpfile.write(content)
    tmpfile.close()
    manifest.append(item % {'id': file_name, 'url': file_name})
    ncx.append(itemref % {'id': file_name})

books = parse_books()
for category in books:#移动每本书的详情到临时目录
    cate_en = category["en"]
    for book in category["books"]:
        pingyin = book[0]
        file_name = cate_en + '_' + pingyin + '.html'
        file_path = 'htmls/' + file_name
        with open(file_path, 'r') as src, open('tmp/OPS/%s' % file_name, 'w') as dst:
            dst.write(src.read())

manifest='\n'.join(manifest)
ncx='\n'.join(ncx)

tmpfile = open('tmp/OPS/content.opf', 'w')
tmpfile.write(opfcontent %{'metadata': metadata, 'manifest': manifest, 'ncx': ncx,})
tmpfile.close()

ncx = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head>
  <meta name="dtb:uid" content=" "/>
  <meta name="dtb:depth" content="-1"/>
  <meta name="dtb:totalPageCount" content="0"/>
  <meta name="dtb:maxPageNumber" content="0"/>
</head>
 <docTitle><text>%(title)s</text></docTitle>
 <docAuthor><text>%(creator)s</text></docAuthor>
<navMap>
%(navpoints)s
</navMap>
</ncx>
'''

navpoint = '''<navPoint id='%s' class='level1' playOrder='%d'>
<navLabel> <text>%d.%s</text> </navLabel>
<content src='%s'/></navPoint>'''

navpoints = []
for i, htmlitem in enumerate(nav_list):
    file_name = htmlitem[0]
    zh = htmlitem[1]
    navpoints.append(navpoint % (file_name, i+1,i+1, zh, file_name))

tmpfile = open('tmp/OPS/content.ncx', 'w')
tmpfile.write(ncx % {
    'title': title,
    'creator': creator,
    'navpoints': '\n'.join(navpoints)})
tmpfile.close()

from zipfile import ZipFile
epubfile = ZipFile('book.epub', 'w')
os.chdir('tmp')
for d, ds, fs in os.walk('.'):
    for f in fs:
        epubfile.write(os.path.join(d, f))
epubfile.close()

shutil.rmtree("../tmp")

logger.info("完成！")