from rest_framework import serializers
from django.conf import settings
from django.core.cache import cache

from models import Cat, Manga, Author, MangaCat, MangaChapter

import datetime

CACHE_TIMEOUT_MAX=60*60*24*30*12 # 1 Year
CACHE_TIMEOUT_WEE=60*60*24*7 # 1 Week
CACHE_TIMEOUT_DAY=60*60*24 # 1 Week

class BaseSerializers(serializers.HyperlinkedModelSerializer):
	createdAt = serializers.SerializerMethodField('format_createdAt')
	updatedAt = serializers.SerializerMethodField('format_updatedAt')

	def format_createdAt(self, obj):
		return datetime.datetime.strftime(obj.createdAt, '%Y-%m-%d %H:%M:%S')

	def format_updatedAt(self, obj):
		return datetime.datetime.strftime(obj.updatedAt, '%Y-%m-%d %H:%M:%S')



class CatSerializers(BaseSerializers):

	class Meta:
		model = Cat
		fields = ('id', 'title', 'slug')

class AuthorSerializers(BaseSerializers):

	class Meta:
		model = Author
		fields = ('id', 'title', 'slug')

class MangaCatSerializers(BaseSerializers):

	class Meta:
		model = MangaCat
		fields = ('catId', 'catTitle','catSlug')

class MangaChapterSerializers(BaseSerializers):

	class Meta:
		model = MangaChapter
		fields = ('series', 'title')

class MangaSerializers(BaseSerializers):
	author = serializers.SerializerMethodField('get__author')
	cat = serializers.SerializerMethodField('get__cat')
	image = serializers.SerializerMethodField('get__image')
	# image2x = serializers.SerializerMethodField('get__image2x')
	# image3x = serializers.SerializerMethodField('get__image3x')

	class Meta:
		model = Manga
		fields = ('id','title','slug','description','author','cat','chapterTotal','chapterCurrent','chapterStatus','image','view',)


	def get__author(self, obj):
		authorId = obj.authorId
		key = 'author:%s' % authorId
		_author = cache.get(key)
		if not _author:
			_author = AuthorSerializers(Author.objects.get(id=obj.authorId)).data
			cache.set(key, _author, CACHE_TIMEOUT_MAX)

		return _author;
		
	def get__cat(self, obj):
		mangaId = obj.id
		key = 'manga_cat:%s' % mangaId
		_manga_cat = cache.get(key)
		if not _manga_cat:
			_manga_cat = MangaCatSerializers(MangaCat.objects.filter(mangaId=mangaId), many=True).data
			cache.set(key, _manga_cat, CACHE_TIMEOUT_MAX)

		return _manga_cat;

	def get__image(self, obj):
		files = dict()
		return {
			'1x' : settings.ROOT_STATIC + 'backdrop/' + obj.image1x, 
			'2x' : settings.ROOT_STATIC + 'backdrop/' + obj.image2x, 
			'3x' : settings.ROOT_STATIC + 'backdrop/' + obj.image3x, 
		}
		


class MangaUpdateSerializers(MangaSerializers):
	lastChapter = serializers.SerializerMethodField('get__lastChapter')


	def get__lastChapter(self, obj):
		mangaId = obj.id
		chapterCurrent = obj.chapterCurrent
		key = 'manga_lastChapter:%s-series:%s' % (mangaId,chapterCurrent)
		_lastChapter = cache.get(key)
		if not _lastChapter:
			_lastChapter = MangaChapterSerializers(MangaChapter.objects.get(mangaId=mangaId, series=chapterCurrent)).data
			cache.set(key, _lastChapter, CACHE_TIMEOUT_DAY)

		return _lastChapter;

	class Meta:
		model = MangaSerializers.Meta.model
		fields = MangaSerializers.Meta.fields + ('lastChapter',)

class MangaDetailSerializers(MangaSerializers):
	lastChapter = serializers.SerializerMethodField('get__lastChapter')


	def get__lastChapter(self, obj):
		mangaId = obj.id
		chapterCurrent = obj.chapterCurrent
		key = 'manga_lastChapter:%s-series:%s' % (mangaId,chapterCurrent)
		_lastChapter = cache.get(key)
		if not _lastChapter:
			_lastChapter = MangaChapterSerializers(MangaChapter.objects.get(mangaId=mangaId, series=chapterCurrent)).data
			cache.set(key, _lastChapter, CACHE_TIMEOUT_DAY)

		return _lastChapter;

	class Meta:
		model = MangaSerializers.Meta.model
		fields = MangaSerializers.Meta.fields + ('lastChapter',)

class MangaChapterDetailSerializers(BaseSerializers):
	content = serializers.SerializerMethodField('get__content')

	def get__content(self, obj):
		id = obj.id
		file_dir = settings.DOCKER_CONTENT_ROOT + 'content/' + str(id) + '.txt'
		from path import path
		file_content = path(file_dir).bytes()
		
		return file_content;

	class Meta:
		model = MangaChapter
		fields = ('id','series','title','content',)

# class ChapterLast5Serializers(BaseSerializers):
# 	lastChapter = serializers.SerializerMethodField('get__lastChapter')


# 	def get__lastChapter(self, obj):
# 		mangaId = obj.id
# 		chapterCurrent = obj.chapterCurrent
# 		key = 'manga_lastChapter:%s-series:%s' % (mangaId,chapterCurrent)
# 		_lastChapter = cache.get(key)
# 		if not _lastChapter:
# 			_lastChapter = MangaChapterSerializers(MangaChapter.objects.get(mangaId=mangaId, series=chapterCurrent)).data
# 			cache.set(key, _lastChapter, CACHE_TIMEOUT_DAY)

# 		return _lastChapter;

# 	class Meta:
# 		model = MangaSerializers.Meta.model
# 		fields = MangaSerializers.Meta.fields + ('lastChapter',)

# class ImageSerializers(serializers.HyperlinkedModelSerializer):
# 	class Meta:
# 		model = Image
# 		fields = ('id','urlLink','urlPreviewLink','caption')

# class ImagePostSerializers(serializers.HyperlinkedModelSerializer):
# 	files_avai = serializers.SerializerMethodField('get_files')

# 	class Meta:
# 		model = Image
# 		fields = ('id','urlLink','image_url_preview','image_url_preview_1x','image_url_preview_2x','caption', 'files_avai')


# 	def get_files(self, obj):
# 		files = dict()
# 		list_size = str(obj.sizeAvai).split(',')
# 		obj.sizeAvai = list_size
# 		for size in list_size:
# 			files[size] = '/'.join([settings.MEDIA_ROOT,obj.fileDir,str(size),obj.fileName])
# 		return files;


# class PostSerializers(BaseSerializers):
# 	user = serializers.SerializerMethodField('get_info_user')
# 	images = serializers.SerializerMethodField('get_list_images')
# 	class Meta:
# 		model = Post
# 		fields = ('id', 'contentText','user','images','public','totalImg','createdAt','updatedAt')

# 	def get_info_user(self, obj):
# 		return UserSerializers(User.objects.get(id=obj.userId)).data

# 	def get_list_images(self, obj):
# 		list_images = ImagePostSerializers(Image.objects.filter(postId=obj.id), many=True).data
# 		return list_images
