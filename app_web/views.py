from django.shortcuts import render, render_to_response

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from helper import RenderPage, NaviPage
from app_web.models import Cat, Manga, MangaChapter,MangaCat, View, Author
from app_web.serializers import \
	CatSerializers, \
	MangaSerializers, MangaUpdateSerializers, MangaDetailSerializers, MangaChapterSerializers,MangaChapterDetailSerializers, \
	AuthorSerializers
from django.core.cache import cache
import traceback
from django.db.models import Q
import  json


CACHE_TIMEOUT_MAX=60*60*24*30*12 # 1 Year
CACHE_TIMEOUT_MON=60*60*24*30 # 1 Week
CACHE_TIMEOUT_WEE=60*60*24*7 # 1 Week
CACHE_TIMEOUT_DAY=60*60*24 # 1 Week

COOKIE_TIMEOUT_WEE=60*60*24*7 # 1 Week


class Home():
	def __init__(self):
		# Categories
		key = 'categories';
		_cat = cache.get(key)
		if not _cat:
			_cat = CatSerializers(Cat.objects.all(), many=True).data
			cache.set(key, _cat, CACHE_TIMEOUT_WEE)

		# Base variables 
		self.res = {
			'categories': _cat,
			'root': 'http://truyen.dev:81/'
		}
	def home(self,request):
		# Manga HOT
		# key_manga_hot = 'manga_hot'
		# manga_hot = cache.get(key_manga_hot)
		# if not manga_hot:
		# 	manga_hot = MangaSerializers(Manga.objects.filter( status__gte=0).order_by('-view')[0:16], many=True).data
		# 	cache.set(key_manga_hot,manga_hot, CACHE_TIMEOUT_WEE)
		key_manga_hot = 'manga_hot'
		manga_hot = cache.get(key_manga_hot)
		if not manga_hot:
			try:
				sql = """
					SELECT id, COUNT(*) as top_view 
					FROM app_web_view
					WHERE createdAt > DATE_FORMAT(DATE_ADD(NOW(), INTERVAL -7 DAY),'%%Y-%%m-%%d') 
					GROUP BY mangaId ORDER BY top_view DESC 
					LIMIT 16
					;
					"""

				manga_hot = MangaCat.objects.raw(sql)
				manga_hot = [manga.id for manga in manga_hot]
				manga_hot = MangaSerializers(Manga.objects.filter(id__in=manga_hot), many=True).data

				cache.set(key_manga_hot,manga_hot, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				pass

		# Manga FULL
		key_manga_full = 'manga_full'
		manga_full = cache.get(key_manga_full)
		if not manga_full:
			manga_full = MangaSerializers(Manga.objects.filter(chapterStatus='FULL', status__gte=0)[:8], many=True).data
			cache.set(key_manga_full,manga_full, CACHE_TIMEOUT_WEE)

		# Manga UPDATE
		key_manga_update = 'manga_update'
		manga_update = cache.get(key_manga_update)
		if not manga_update:
			manga_update = MangaUpdateSerializers(Manga.objects.filter( status__gte=0).order_by('-updatedAt')[0:16], many=True).data
			cache.set(key_manga_update,manga_update, CACHE_TIMEOUT_WEE)

		# Manga NEW
		key_manga_new = 'manga_new'
		manga_new = cache.get(key_manga_new)
		if not manga_new:
			manga_new = MangaSerializers(Manga.objects.filter( status__gte=0).order_by('-createdAt')[0:16], many=True).data
			cache.set(key_manga_new,manga_new, CACHE_TIMEOUT_WEE)

		# Readed manga chapter
		manga_readed = request.COOKIES.get('readed') 
		if manga_readed:
			try:
				manga_readed = json.loads(manga_readed)
			except Exception as e:
				manga_readed = []
		else:
			manga_readed = []
		print manga_readed

		for a in manga_readed:
			print a


		self.res['manga_hot'] = manga_hot
		self.res['manga_full'] = manga_full
		self.res['manga_new'] = manga_new
		self.res['manga_update'] = manga_update
		self.res['manga_readed'] = manga_readed
		# return JsonResponse({'a':manga_readed})
		return render_to_response('home/index.html', self.res)

	def manga(self, request,manga_slug, page=1):
		page = str(page).replace('.html','')
		try:
			page = int(page)
		except Exception as e:
			return HttpResponseRedirect("/trang-khong-ton-tai.html")

		page = RenderPage(page)

		manga_slug = manga_slug.replace('.html','')
		key_manga = 'manga_detail:%s' % manga_slug
		_manga = cache.get(key_manga)
		if not _manga:
			try:
				_manga = MangaDetailSerializers(Manga.objects.get(slug=manga_slug, status__gte=0)).data
				cache.set(key_manga,_manga, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass

		manga_id = _manga['id']
		chapter_current = _manga['chapterCurrent'] 
		chapter_total = _manga['chapterTotal'] 

		# Gen Navi page
		chapter_page_navi = NaviPage(chapter_total, page['page'])

		# Last 5 chapter
		key_last5chapter = 'manga:%s-last5chapter:%s' % (manga_id, chapter_current)
		_last5chapter = cache.get(key_last5chapter)
		if not _last5chapter:
			_last5chapter = MangaChapterSerializers(MangaChapter.objects.filter(status__gte=0, mangaId=manga_id).order_by('-series')[0:6], many=True).data
			cache_timeout = CACHE_TIMEOUT_WEE if chapter_total==chapter_current else CACHE_TIMEOUT_DAY
			cache.set(key_last5chapter, _last5chapter, cache_timeout)

		# Chapter
		key_chapter_page = 'manga:%s-chapter_page:%s' % (manga_id, page['page'])
		_chapter_page = cache.get(key_chapter_page)
		if not _chapter_page:
			_chapter_page = MangaChapterSerializers(MangaChapter.objects.filter(mangaId=manga_id).order_by('series')[page['offset']: page['limit']], many=True).data
			cache.set(key_chapter_page, _chapter_page, CACHE_TIMEOUT_MAX)


		authorId = _manga['author']['id']
		# Manga same author
		key_manga_same_author = 'manga-same-author:author_id:%s' % authorId
		_manga_same_author = cache.get(key_manga_same_author)
		if not _manga_same_author:
			_manga_same_author = MangaSerializers(Manga.objects.filter(authorId=authorId).order_by('view')[0:6], many=True).data
			cache.set(key_manga_same_author, _manga_same_author, CACHE_TIMEOUT_MAX)

		cats = _manga['cat']
		cats = [str(cat['catId']) for cat in cats]
		cats_str = ','.join(cats)
		# Manga same author
		key_manga_same_cat = 'manga-same-cat:cat_id:%s' % cats_str
		_manga_same_cat = cache.get(key_manga_same_cat)
		if not _manga_same_cat:

			key_manga_cat = 'manga-cat:cat_id:%s' % cats_str
			_manga_cat = cache.get(key_manga_cat)
			if not _manga_same_cat:
				_manga_cat = MangaCat.objects.filter(catId__in=cats).order_by('?')[:5]
				_manga_cat = [manga_cat.mangaId for manga_cat in _manga_cat]
				cache.set(key_manga_same_cat, _manga_same_cat, CACHE_TIMEOUT_DAY)

			print manga_cat
			_manga_same_cat = MangaSerializers(Manga.objects.filter(id__in=_manga_cat, status__gte=0).order_by('view')[0:6], many=True).data
			cache.set(key_manga_same_cat, _manga_same_cat, CACHE_TIMEOUT_MAX)

		_manga['last5chapter'] = _last5chapter
		_manga['chapter_page'] = _chapter_page
		_manga['chapter_page'] = _chapter_page
		_manga['chapter_page_navi'] = chapter_page_navi
		_manga['manga_same_author'] = _manga_same_author
		_manga['manga_same_cat'] = _manga_same_cat

		try:
			manga = Manga.objects.get(id=manga_id)
			manga.view = manga.view + 1
			manga.save()
			manga_view = View.objects.create(
				mangaId=manga_id)
			manga_view.save()
		except Exception as e:
			traceback.print_exc()
			pass

		self.res['manga'] = _manga
		# return JsonResponse({'manga':_manga})
		return render_to_response('manga/index.html', self.res)


	def chapter(self, request, manga_slug, series):


		series = str(series).replace('.html','')
		try:
			series = int(series)
		except Exception as e:
			return HttpResponseRedirect("/trang-khong-ton-tai.html")

		key_manga = 'manga_detail:%s' % manga_slug
		_manga = cache.get(key_manga)
		if not _manga:
			try:
				_manga = MangaDetailSerializers(Manga.objects.get(slug=manga_slug, status__gte=0)).data
				cache.set(key_manga,_manga, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")

		manga_id = _manga['id']
		chapter_current = _manga['chapterCurrent']

		# Get Chapter
		key_chapter = 'manga_chapter:%s-chapter:%s' % (manga_id,series)
		_chapter = cache.get(key_chapter)
		if not _chapter:
			try:
				_chapter = MangaChapterDetailSerializers(MangaChapter.objects.get(mangaId=manga_id, series=series)).data
				cache.set(key_chapter,_chapter, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")

		chapter_attr = {
			'next_series': None,
			'prev_series': None,
			'max_series': chapter_current,
			'curr_series': series
		}
		series_next = None
		if chapter_current > series:
			series_next_series = series + 1
			chapter_attr['next_series'] = series_next_series
			key_series_next = 'manga_chapter:%s-chapter-next:%s' % (manga_id,series_next_series)
			series_next = cache.get(key_series_next)
			if not series_next:
				try:
					series_next = MangaChapterSerializers(MangaChapter.objects.get(mangaId=manga_id, series=series_next_series)).data
					cache.set(key_series_next,series_next, CACHE_TIMEOUT_WEE)
				except Exception as e:
					series_next = None

		if series > 1:
			chapter_attr['prev_series'] = series - 1

		_chapter['attr'] = chapter_attr

		try:
			manga = Manga.objects.get(id=manga_id)
			manga.view = manga.view + 1
			manga.save()
			manga_view = View.objects.create(
				mangaId=manga_id)
			manga_view.save()
		except Exception as e:
			traceback.print_exc()
			pass


		readed_cookie = request.COOKIES.get('readed') 

		if not readed_cookie:
			readed_cookie = {}
		else:
			try:
				readed_cookie = json.loads(readed_cookie)
			except Exception as e:
				readed_cookie = {}

		readed_chapter = {
			'manga': manga_id,
			'series' : series,
			'title' : _manga['title'],
			'slug' : _manga['slug'],
			'series_next' : series_next,
		}
		if chapter_current <= series:
			readed_cookie.pop(unicode(str(manga_id)), None)
		else:
			readed_cookie[unicode(str(manga_id))] = readed_chapter
		readed_cookie = json.dumps(readed_cookie)

		self.res['manga'] = _manga
		self.res['chapter'] = _chapter
		# return JsonResponse({'manga':_chapter})

		response = render_to_response('manga/chapter.html', self.res)
		response.set_cookie("readed",readed_cookie,max_age=COOKIE_TIMEOUT_WEE)
		return response

	def cat(self,request, cat_slug, page=1):

		_sort = request.GET.get('sort', 'top')
		sort = _sort
		list_sort = {
			'default' : 'view',
			'top' : 'view',
			'new' : 'createdAt'
		}
		if sort in list_sort:
			sort = list_sort[sort]
		else:
			sort = list_sort['default']

		page = str(page).replace('.html','')
		try:
			page = int(page)
		except Exception as e:
			return HttpResponseRedirect("/trang-khong-ton-tai.html")

		page = RenderPage(page,16)

		# Get Cat info
		cat_slug = cat_slug.replace('.html','')
		key_cat = 'cat:%s' % cat_slug
		_cat = cache.get(key_cat)
		if not _cat:
			try:
				_cat = CatSerializers(Cat.objects.get(slug=cat_slug, status__gte=0)).data
				cache.set(key_cat,_cat, CACHE_TIMEOUT_MON)
			except Exception as e:
				traceback.print_exc()
				# return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass

		cat_id = _cat['id']

		# Cat manga total
		key_cat_manga_total = 'cat_manga_total:%s' % cat_id
		_cat_manga_total = cache.get(key_cat_manga_total)
		if not _cat_manga_total:
			_cat_manga_total = MangaCat.objects.filter(catId=cat_id, status__gte=0).count()
			cache.set(key_cat_manga_total,_cat_manga_total, CACHE_TIMEOUT_WEE)

		cat_manga_page_navi = NaviPage(_cat_manga_total, page['page'], 16)

		# Cat manga pagination
		key_cat_manga = 'cat_manga:%s-sort:%s-page:%s' % (cat_id,sort, page['page'])
		_cat_manga = cache.get(key_cat_manga)
		if not _cat_manga:
			try:
				sql = """
					SELECT m.* \
					FROM \
						truyen_v2.app_web_mangacat mc \
						JOIN truyen_v2.app_web_manga m ON m.id = mc.mangaId \
					WHERE mc.catId = {0} \
					ORDER BY m.{1}  DESC \
					LIMIT {2},{3}
					""".format(cat_id, sort, page['offset'], page['limit'] - page['offset'])

				_cat_manga = MangaCat.objects.raw(sql)
				_cat_manga = MangaSerializers(_cat_manga, many=True).data

				cache.set(key_cat_manga,_cat_manga, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass


		# Cat manga top view
		key_cat_manga_top = 'cat_manga_top_top:%s' % (cat_id)
		_cat_manga_top = cache.get(key_cat_manga_top)
		if not _cat_manga_top:
			try:
				sql = """
					SELECT m.* \
					FROM \
						truyen_v2.app_web_mangacat mc \
						JOIN truyen_v2.app_web_manga m ON m.id = mc.mangaId \
					WHERE mc.catId = {0} \
					ORDER BY m.view  DESC \
					LIMIT 10
					""".format(cat_id, sort, page['offset'], page['limit'])

				_cat_manga_top = MangaCat.objects.raw(sql)
				_cat_manga_top = MangaSerializers(_cat_manga_top, many=True).data

				cache.set(key_cat_manga_top,_cat_manga_top, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass
		attr = {
			'sort' : _sort,
			'page' : cat_manga_page_navi,
		}
		_cat['attr'] = attr
		self.res['cat'] = _cat
		self.res['cat_manga'] = _cat_manga
		self.res['cat_manga_top'] = _cat_manga_top
		# return JsonResponse({'manga':page})
		return render_to_response('cat/index.html', self.res)

	def author(self,request, author_slug, page=1):

		_sort = request.GET.get('sort', 'top')
		sort = _sort
		list_sort = {
			'default' : 'view',
			'top' : 'view',
			'new' : 'createdAt'
		}
		if sort in list_sort:
			sort = list_sort[sort]
		else:
			sort = list_sort['default']

		page = str(page).replace('.html','')
		try:
			page = int(page)
		except Exception as e:
			return HttpResponseRedirect("/trang-khong-ton-tai.html")

		page = RenderPage(page,24)

		# Get Cat info
		author_slug = author_slug.replace('.html','')
		key_author = 'cat:%s' % author_slug
		_author = cache.get(key_author)
		print author_slug
		if not _author:
			try:
				_author = AuthorSerializers(Author.objects.get(slug=author_slug, status__gte=0)).data
				cache.set(key_author,_author, CACHE_TIMEOUT_MON)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass

		author_id = _author['id']

		# Cat manga total
		key_author_manga_total = 'author_manga_total:%s' % author_id
		_author_manga_total = cache.get(key_author_manga_total)
		if not _author_manga_total:
			_author_manga_total = Manga.objects.filter(authorId=author_id, status__gte=0).count()
			cache.set(key_author_manga_total,_author_manga_total, CACHE_TIMEOUT_WEE)

		author_manga_page_navi = NaviPage(_author_manga_total, page['page'], 24)

		# Cat manga pagination
		key_author_manga = 'cat_manga:%s-sort:%s-page:%s' % (author_id,sort, page['page'])
		_author_manga = cache.get(key_author_manga)
		if not _author_manga:
			try:
				_author_manga = MangaSerializers(Manga.objects.filter(authorId=author_id, status__gte=0).order_by(sort)[page['offset']:page['limit']], many=True).data

				cache.set(key_author_manga,_author_manga, CACHE_TIMEOUT_WEE)
			except Exception as e:
				traceback.print_exc()
				return HttpResponseRedirect("/trang-khong-ton-tai.html")
				pass

		attr = {
			'sort' : _sort,
			'page' : author_manga_page_navi,
		}
		_author['attr'] = attr
		self.res['author'] = _author
		self.res['author_manga'] = _author_manga
		# return JsonResponse({'manga':self.res})
		return render_to_response('author/index.html', self.res)


	def search(self, request):
		key = request.GET.get('k', None)
		attr = {
			'key' : key,
			'result' : []
		}
		if key is None or key == '':
			return JsonResponse(attr)
		else:
			key_search_manga = 'manga_search:%s' % key
			_manga_search = cache.get(key_search_manga)
			if not _manga_search:
				try:
					a = Manga.objects.filter(title__icontains=key, status__gte=0).order_by('-view')[:10]
					print a.query
					_manga_search = MangaSerializers(Manga.objects.filter(title__icontains=key, status__gte=0).order_by('-view')[:10], many=True).data
					cache.set(key_search_manga,_manga_search, CACHE_TIMEOUT_WEE)
				except Exception as e:
					return JsonResponse(attr)

		attr['result'] = _manga_search
		return JsonResponse(attr)

	def error(self, request):
		return render_to_response('errors/404.html', self.res)















