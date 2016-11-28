from __future__ import unicode_literals

from django.db import models

# Create your models here.



class BaseModels(models.Model):
	id        = models.AutoField(primary_key=True)
	status    = models.IntegerField(default=0)
	createdAt = models.DateTimeField(auto_now_add=True)
	updatedAt = models.DateTimeField(auto_now_add=True)
	class Meta:
		abstract = True
		unique_together = ['id']
		ordering = ['createdAt']


class Manga(BaseModels):

	title 	            = models.CharField(max_length=255)
	slug 	            = models.CharField(max_length=255)
	description         = models.TextField(max_length=1000, blank=True, null=True)
	authorId             = models.IntegerField()
	chapterTotal       = models.IntegerField(default=0)
	chapterCurrent     = models.IntegerField(default=0)
	chapterStatus       = models.CharField(max_length=32, null=True)
	source              = models.CharField(max_length=32, null=True)
	sourceLink         = models.CharField(max_length=255, null=True)
	image               = models.CharField(max_length=100)
	image1x             = models.CharField(max_length=100)
	image2x             = models.CharField(max_length=100)
	image3x             = models.CharField(max_length=100)
	imageThumb          = models.CharField(max_length=100)
	type                = models.CharField(max_length=100, default=0)
	view = models.IntegerField(default=0)

class MangaCat(BaseModels):
	catId    = models.IntegerField()
	catTitle    = models.CharField(max_length=255, null=True)
	catSlug    = models.CharField(max_length=255, null=True)
	mangaId    = models.IntegerField()

class Cat(BaseModels):
	title 	            = models.CharField(max_length=255)
	slug 	            = models.CharField(max_length=255)
	totalManga 		= models.IntegerField(default=0)

class Author(BaseModels):
	title 	            = models.CharField(max_length=255)
	slug 	            = models.CharField(max_length=255)
	totalManga 		= models.IntegerField(default=0)

class View(BaseModels):
	mangaId    = models.IntegerField()

class MangaChapter(BaseModels):
	title 	            = models.CharField(max_length=255)
	series    = models.IntegerField()
	mangaId    = models.IntegerField()
	type                = models.CharField(max_length=100, null=True)
	sourceLink         = models.CharField(max_length=255, null=True)
	image             = models.CharField(max_length=200, null=True)













