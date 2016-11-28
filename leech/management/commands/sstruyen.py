# coding=utf-8
#-*- coding: utf-8 -*-

import json
import os
import re
import math
import requests
import traceback
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection, connections, transaction
import datetime
from app_web.models import Cat, Manga, MangaCat, Author, MangaChapter

from _extens import Log,ImageHandle
import slugify
from bs4 import BeautifulSoup
import urllib
from django.utils import timezone

# Config

ROOT = 'http://sstruyen.com'
CHAPTER_OFFSET = 50

_cates = [
    {'url': '/doc-truyen/ngon-tinh', 'title': u'Ngôn tình'},
    {'url': '/doc-truyen/truyen-teen', 'title': u'Truyện Teen'},
    {'url': '/doc-truyen/xuyen-khong', 'title': u'Xuyên Không'},
    {'url': '/doc-truyen/trong-sinh',  'title': u'Trọng Sinh'},
    {'url': '/doc-truyen/kiem-hiep',   'title': u'Kiếm Hiệp'},
    {'url': '/doc-truyen/tien-hiep',   'title': u'Tiên Hiệp'},
    {'url': '/doc-truyen/sac-hiep',    'title': u'Sắc Hiệp'},
    {'url': '/doc-truyen/lich-su',     'title': u'Lịch Sử'},
    {'url': '/doc-truyen/quan-su',     'title': u'Quân Sự'},
    {'url': '/doc-truyen/do-thi',      'title': u'Đô Thị'},
    {'url': '/doc-truyen/vong-du',     'title': u'Võng Du'},
    {'url': '/doc-truyen/di-gioi',     'title': u'Dị Giới'},
    {'url': '/doc-truyen/di-nang',     'title': u'Dị Năng'},
    {'url': '/doc-truyen/khoa-huyen',  'title': u'Khoa Huyễn'},
    {'url': '/doc-truyen/huyen-huyen', 'title': u'Huyền Huyễn'},
    {'url': '/doc-truyen/trinh-tham',  'title': u'Trinh Thám'},
    {'url': '/doc-truyen/truyen-ma',   'title': u'Truyện Ma'},
    {'url': '/doc-truyen/dam-my',      'title': u'Đam Mỹ'},
    {'url': '/doc-truyen/nu-cuong',    'title': u'Nữ Cường'},
    {'url': '/doc-truyen/nu-phu',      'title': u'Nữ Phụ'},
    {'url': '/doc-truyen/bach-hop',    'title': u'Bách Hợp'},
    {'url': '/doc-truyen/tieu-thuyet', 'title': u'Tiểu Thuyết'}
]



class Command(BaseCommand):
    help = 'Migrate data insight'
    def create_parser(self, prog_name, subcommand):

       
        return super(Command, self).create_parser(prog_name, subcommand)
    def handle(self, *args, **options):
        self.leech()

    def leech(self):
        Log().Info('Start leech sstruyen')

        self.manga('http://sstruyen.com/doc-truyen/vat-hy-sinh-nu-phu-ga-lan-hai-cong-chiem/11005.html')
        # self.manga_from_cat()

    def manga_from_cat(self):
        for cat in _cates:
            cat_source = ROOT + cat['url'] + '.html'
            cat_title = cat['title']
            cat_slug = slugify.slugify(cat_title)

            # insert cat
            _cat = Cat.objects.get_or_create(
                title=cat_title,
                slug=cat_slug,
                )
            cat_id = _cat[0].id

            try:
                Log().Info('Start leech cat %s ' % cat_source)
                cat_content = requests.get(cat_source)
                cat_content = BeautifulSoup(cat_content.text,'html.parser')
                cat_pages = cat_content.find('div',{'class': 'page-split'})
                cat_page_curr = cat_pages.find('a', {'class' : 'items active'}).text
                cat_pages = cat_pages.findAll('a');
                cat_page_max = cat_pages[-1].text

                for page in xrange(1, int(cat_page_max) + 1):
                    cat_page_source = ROOT + cat['url'] + '/page-' + str(page) + '.html'
                    try:
                        Log().Info('Start leech cat page %s ' % cat_page_source)
                        cat_manga_content = requests.get(cat_page_source)
                        cat_manga_content = BeautifulSoup(cat_manga_content.text,'html.parser')
                        cat_mangas = cat_manga_content.findAll('div', {'class': 'storyinfo'})

                        for cat_manga in cat_mangas:
                            manga_source = cat_manga.find('a')['href']
                            manga_source = ROOT + manga_source

                            self.manga(manga_source)
                    except Exception as e:
                        Log().Error('Get cat manga %s failed: %s' % (cat_page_source, e))




            except Exception as e:
                Log().Error('Get cat page %s failed: %s' % (cat_source, e))
                _cat.update(status=-1)

    def manga(self, manga_source):
        Log().Info('Start leech manga %s ' % manga_source)
        manga_list_props = {
            'tac-gia' : None,
            'the-loai' : None,
            'so-chuong' : None,
            'trang-thai' : None,
            'lan-doc' : None,
        }
        __exits = False

        # Check if manga exist {True: check is Full {True: return | get chapterStatus & leech} | False: leech}
        try:
            _manga = Manga.objects.get(sourceLink=manga_source)
            __exits = True
            if _manga.chapterStatus == 'FULL':
                return True
        except Exception as e:
            pass

        try:
            manga_content = requests.get(manga_source)
            manga_content = BeautifulSoup(manga_content.text,'html.parser')

            manga_info = manga_content.find('div', {'class': 'content1'})
            if __exits == False:
                manga_img = manga_info.find('img')
                manga_img = ROOT + manga_img['src']
                manga_title = manga_info.find('a')
                manga_title = manga_title.text
                manga_descs = manga_info.find('div', {'class': 'story_description'})
                try:
                    manga_descs.find('div').decompose()
                    manga_descs.find('b').decompose()
                except Exception, e:
                    pass
                manga_descs = manga_descs.text
                manga_slug = slugify.slugify(manga_title)

                manga_props = manga_info.findAll('li')
                for manga_prop in manga_props:
                    manga_prop = manga_prop.text.split(':')
                    manga_prop_key =slugify.slugify( manga_prop[0].strip())
                    manga_prop_val = manga_prop[1].strip()
                    if manga_prop_key == 'tac-gia':
                        manga_list_props['tac-gia'] = self.manga_prop_author(manga_prop_val)
                    if manga_prop_key == 'lan-oc':
                        manga_list_props['lan-oc'] = int(manga_prop_val)
                    if manga_prop_key == 'trang-thai':
                        manga_list_props['trang-thai'] = manga_prop_val
                    if manga_prop_key == 'so-chuong':
                        manga_list_props['so-chuong'] = int(manga_prop_val)
                    if manga_prop_key == 'the-loai':
                        manga_list_props['the-loai'] = self.manga_prop_cat(manga_prop_val)

                _manga = Manga.objects.create(
                    title=manga_title,
                    slug=manga_slug,
                    image=manga_img,
                    description=manga_descs,
                    authorId=manga_list_props['tac-gia'],
                    view=manga_list_props['lan-oc'],
                    chapterTotal=manga_list_props['so-chuong'],
                    chapterStatus=manga_list_props['trang-thai'],
                    source=ROOT,
                    sourceLink=manga_source,
                    )
                try:
                    _manga.save()
                    Log().Info('Insert manga %s success' % (manga_source))
                    # Insert cat
                    try:
                        self.manga_cat_insert(manga_list_props['the-loai'], _manga.id)
                    except Exception as e:
                        pass

                    # Update image handle
                    try:
                        image = self.manga_image(manga_img,_manga.id)
                        _manga.image1x = image['image1x']
                        _manga.image2x = image['image2x']
                        _manga.image3x = image['image3x']
                        _manga.imageThumb = image['imageThumb']
                        _manga.save()
                    except Exception as e:
                        _manga.status=-1
                        _manga.save()

                except Exception as e:
                    Log().Error('Insert manga %s failed: %s' % (manga_source, e))
                    return False
            else:
                manga_props = manga_info.findAll('li')
                for manga_prop in manga_props:
                    manga_prop = manga_prop.text.split(':')
                    manga_prop_key =slugify.slugify( manga_prop[0].strip())
                    manga_prop_val = manga_prop[1].strip()
                    if manga_prop_key == 'trang-thai':
                        manga_list_props['trang-thai'] = manga_prop_val
                    if manga_prop_key == 'so-chuong':
                        manga_list_props['so-chuong'] = int(manga_prop_val)
                try:
                    _manga.chapterTotal=manga_list_props['so-chuong']
                    _manga.chapterStatus=manga_list_props['trang-thai']
                    _manga.save()
                    Log().Info('Update manga %s success' % (manga_source,))
                except Exception as e:
                    Log().Error('Update manga %s failed: %s' % (_manga.id, e))


            manga_chapter_info = manga_content.findAll('div', {'class': 'fixContent'})[-1]
            manga_chapter_pages = manga_chapter_info.find('div',{'class':'page-split'})
            try:
                manga_chapter_pages = manga_chapter_pages.findAll('a')
                manga_chapter_pages_max = manga_chapter_pages[-1].text
            except Exception as e:
                manga_chapter_pages_max= 1


            manga_chapter_pages_curr = _manga.chapterCurrent/int(CHAPTER_OFFSET)
            chapter_series = _manga.chapterCurrent;
            for page in xrange(manga_chapter_pages_curr, int(manga_chapter_pages_max)):
                page = '/page-%s.html' % page
                manga_chapter_pages_source = manga_source.replace('.html', page) 
                manga_chapter_curr = _manga.chapterCurrent % CHAPTER_OFFSET
                try:
                    manga_chapter_pages_content = requests.get(manga_chapter_pages_source)
                    manga_chapter_pages_content = BeautifulSoup(manga_chapter_pages_content.text,'html.parser')

                    manga_chapter_sources = manga_chapter_pages_content.findAll('div', {'class': 'chuongmoi'})[-1].findAll('a')
                    for manga_chapter_source in xrange(manga_chapter_curr,len(manga_chapter_sources)):
                        chapter_series+=1
                        manga_chapter_source = manga_chapter_sources[manga_chapter_source]['href']
                        manga_chapter_source = ROOT + manga_chapter_source

                        insert_chapter = self.chapter(manga_chapter_source, _manga.id, chapter_series)
                        if insert_chapter != False:
                            _manga.chapterCurrent = insert_chapter
                            _manga.updatedAt = timezone.now()
                            _manga.save()

                except Exception as e:
                    traceback.print_exc()
                    Log().Error('Get page manga chapter %s failed: %s' % (manga_chapter_pages_source, e))
                

        except Exception as e:
            Log().Error('Get manga content %s failed: %s' % (manga_source, e))


    def manga_prop_author(self, manga_prop_author):
        author_title = manga_prop_author
        author_slug = slugify.slugify(author_title)
        _author = Author.objects.get_or_create(slug=author_slug, title=author_title)
        return _author[0].id

    def manga_prop_cat(self, manga_prop_cats):
        list_cat = []

        manga_prop_cats = manga_prop_cats.split(',')
        for manga_prop_cat in manga_prop_cats:
            cat_slug = slugify.slugify(manga_prop_cat.strip())
            _cat = Cat.objects.get_or_create(slug=cat_slug, title=manga_prop_cat.strip())
            list_cat.append(_cat[0].id)

        return list_cat


    def manga_cat_insert(self, cats, mangaId ):
        for cat in cats:
            try:
                    
                _mangaCat = MangaCat.objects.get_or_create(
                    catId = int(cat),
                    mangaId = int(mangaId),
                    )
            except Exception as e:
                traceback.print_exc()

    def manga_image(self,url, manga):
        manga_id = str(manga)
        image_location = settings.IMAGE % manga_id
        try:
            urllib.urlretrieve(url, image_location)
            ImageHandle().watermark(image_location)
            return ImageHandle().resize(manga_id)
        except Exception as e:
            traceback.print_exc()
            Log().Error('Get manga Image %s failed: %s' % (url, e))
            return False




    def chapter(self, url, manga_id, series):
        try:
            chapter_content = requests.get(url)
            chapter_content = BeautifulSoup(chapter_content.text,'html.parser')

            chapter_content = chapter_content.find('div', {'class': 'detail-content'})
            chapter_title = chapter_content.find('h3').text.strip().replace("'",'')
            
            timestamp = re.search(r'szChapterTime = "(\S+) (\S+)";*', chapter_content.text)
            try:
                timestamp = timestamp.group(1).replace('-','') + timestamp.group(2).replace(':','')
                source_id = url.split('/')[-1].replace('.html','')
                chapter_content = requests.get(ROOT + '/doc-truyen/index.php?ajax=ct&id=%s&t=%s' % (source_id, timestamp) ).text
                soup = BeautifulSoup(chapter_content,'html.parser')
                image = None
                try:
                    is_image = soup.find('img')
                    if is_image is not None:
                        image = is_image['src']
                        type = 'image'
                    else:
                        type = None

                    _chapter = MangaChapter.objects.create(
                        title = chapter_title,
                        series = series,
                        mangaId = manga_id,
                        type=type,
                        image=image,
                        sourceLink=url,
                        )
                    _chapter.save()

                    CHAPTER_CONTENT = open(settings.CONTENT_ROOT + '%s.txt' % _chapter.id, 'w')
                    CHAPTER_CONTENT.write(chapter_content.encode('utf-8'))
                    CHAPTER_CONTENT.close()

                    Log().Info('Get manga chapter %s success' % url)
                    return series
                except Exception, e:
                    traceback.print_exc()
                    return False
            except Exception, e:
                traceback.print_exc()
                return False



        except Exception as e:
            traceback.print_exc()
            Log().Error('Get  chapter content %s failed: %s' % (url, e))
            return False













#update platform