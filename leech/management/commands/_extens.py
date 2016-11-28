__author = 'quyench'

import datetime

# Fn extensions
# coding=utf-8
# Leech truyenfull.com

import os
try:
    from PIL import Image,ImageEnhance
except:
    import Image,ImageEnhance
from django.conf import settings

# from config.local import IMAGE_DIR,IMAGE_CONTENT_DIR

SIZES = [
    ['image1x',180, False],
    ['image2x',100, False],
    ['image3x',60, False],
    ['imageThumb',60,True],
]

class ImageHandle():
	def watermark(self,link):
	    im = Image.open(link)
	    mark = Image.open(settings.IMAGE_WT)
	    im = im.crop((0, 0, 160, 210))
	    if im.mode != 'RGBA':
	        im = im.convert('RGBA')
	    layer = Image.new('RGBA', im.size, (0,0,0,0))
	    layer.paste(mark, (0,im.size[1] -43))
	    newImage = Image.composite(layer, im, layer)
	    return newImage.save(link)

	def resize(self,id):
	    file_name = settings.IMAGE % id
	    list_images = {}
	    im = Image.open(file_name)
	    for size in SIZES:
	        o_w, o_h = im.size
	        n_w = size[1]
	        n_h = n_w * o_h / o_w
	        img = im.resize((n_w,n_h), Image.ANTIALIAS)
	        image_resize_name =  str(id) + '-' + size[0]
	        image_resize_fullname = settings.IMAGE % image_resize_name
	        image_resize_name = settings.IMAGE_NAME % image_resize_name
	        img.save(image_resize_fullname)
	        list_images[size[0]] = image_resize_name
	    return list_images


class Log():

	def __init__(self):
		pass

	def Info(self,msg):
		print "[INFO] - %s : %s " % (datetime.datetime.now(), msg,)
	def Error(self,msg):
		print "[ERROR] - %s : %s " % (datetime.datetime.now(), msg,)
	def Done(self,msg):
		print "[DONE] - %s : %s " % (datetime.datetime.now(), msg,)
