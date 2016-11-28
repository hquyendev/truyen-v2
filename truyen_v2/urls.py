"""truyen_v2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app_web import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Root
	url(r'^$', views.Home().home, name='home'),
    # Manga
    url(r'^truyen/(?P<manga_slug>([a-z0-9-.]+))$', views.Home().manga, name='manga' ),
    url(r'^truyen/(?P<manga_slug>([a-z0-9-.]+))/page-(?P<page>([a-z0-9-.]+)+)$', views.Home().manga, name='manga' ),
    url(r'^truyen/(?P<manga_slug>([a-z0-9-.]+))/chuong/(?P<series>([a-z0-9-.]+)+)$', views.Home().chapter, name='chapter' ),
    # Cat
    url(r'^the-loai/(?P<cat_slug>([a-z0-9-.]+))$', views.Home().cat, name='cat' ),
    url(r'^the-loai/(?P<cat_slug>([a-z0-9-.]+))/page-(?P<page>([a-z0-9-.]+)+)$', views.Home().cat, name='cat-manga' ),
    # Author
    url(r'^tac-gia/(?P<author_slug>([a-z0-9-.]+))$', views.Home().author, name='author' ),
    url(r'^tac-gia/(?P<author_slug>([a-z0-9-.]+))/page-(?P<page>([a-z0-9-.]+)+)$', views.Home().author, name='author-manga' ),
    # Search
    url(r'^tim-kiem/$', views.Home().search, name='search' ),


    url(r'^trang-khong-ton-tai.html$', views.Home().error),
]
