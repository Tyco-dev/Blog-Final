"""MyBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from marketing.views import contactView, successView
from posts.views import index, blog, post, search, post_delete, post_update, post_create, CategoryCreate, delete_category

urlpatterns = [
    path('admin/', admin.site.urls),

    # Index/Home url
    path('', index, name='index'),

    # Account urls
    path('accounts/', include('allauth.urls')),

    # Blog post urls
    path('blog/', blog, name='post_list'),
    path('search/', search, name='search'),
    path('post/<id>/', post, name='post_detail'),
    path('create/', post_create, name='post_create'),
    path('post/<id>/update/', post_update, name='post_update'),
    path('post/<id>/delete/', post_delete, name='post_delete'),
    path('create_category/', CategoryCreate.as_view(), name='category_create'),
    path('delete/<title>/', delete_category, name='delete_category'),

    # Contact urls
    path('contact/', contactView, name='contact'),
    path('success/', successView, name='success'),

    #Ckeditor url
    path('ckeditor/', include('ckeditor_uploader.urls'))

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
