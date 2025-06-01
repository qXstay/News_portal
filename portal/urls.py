from datetime import time

from django.urls import path
from . import views
from .views import (
    NewsCreateView, NewsUpdateView, NewsDeleteView,
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView
)
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('news/', views.news_list, name='news_list'),  # Список новостей
    path('news/<int:post_id>/', views.news_detail, name='news_detail'),  # Детальная страница новости
    path('news/search/', views.search_news, name='news_search'),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('become_author/', views.become_author, name='become_author'),
    path('subscribe/<int:category_id>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<int:category_id>/', views.unsubscribe, name='unsubscribe'),
]

def cache_test(request):
    return HttpResponse("Cache time: " + str(time.time()))