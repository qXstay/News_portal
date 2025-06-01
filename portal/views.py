from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Author, Category
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import NewsForm, ArticleForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .filters import NewsFilter
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
import logging
from .mixins import EmailVerifiedRequiredMixin
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

def authors_only(user):
    return user.groups.filter(name='authors').exists()

@cache_page(60 * 5)  # 5 минут
def news_list(request):
    news = Post.objects.filter(post_type='news').order_by('-created_at')
    paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'portal/news_list.html', {'page_obj': page_obj})

@cache_page(60 * 5)  # 5 минут
def article_list(request):
    articles = Post.objects.filter(post_type='article').order_by('-created_at')
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'portal/article_list.html', {'page_obj': page_obj})

@cache_page(60 * 5)  # 5 минут
def news_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'portal/news_detail.html', {'post': post})

@cache_page(60)  # 1 минута
def home(request):
    return render(request, 'portal/index.html')

def search_news(request):
    news = Post.objects.filter(post_type='news').order_by('-created_at')
    news_filter = NewsFilter(request.GET, queryset=news)
    return render(request, 'portal/search.html', {'filter': news_filter, 'news': news_filter.qs})

class NewsCreateView(LoginRequiredMixin, EmailVerifiedRequiredMixin, CreateView):
    model = Post
    form_class = NewsForm
    template_name = 'portal/post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'news'
        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author
        post.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'news'
        return context


class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = NewsForm
    template_name = 'portal/post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'news'
        return context

class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'portal/post_delete.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        return self.get_object().author.user == self.request.user

@method_decorator(user_passes_test(authors_only, login_url='become_author'), name='dispatch')
class ArticleCreateView(LoginRequiredMixin, EmailVerifiedRequiredMixin, CreateView):
    model = Post
    form_class = ArticleForm
    template_name = 'portal/post_edit.html'
    success_url = reverse_lazy('article_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'article'
        author, _ = Author.objects.get_or_create(user=self.request.user)
        post.author = author
        post.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'article'
        return context

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = ArticleForm
    template_name = 'portal/post_edit.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        return self.get_object().author.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'article'
        return context

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'portal/post_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        return self.get_object().author.user == self.request.user

@login_required
def become_author(request):
    user = request.user
    authors_group, created = Group.objects.get_or_create(name='authors')
    if not user.groups.filter(name='authors').exists():
        user.groups.add(authors_group)
    return redirect('home')

@login_required
def subscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.subscribers.add(request.user)
    return redirect('news_list')

@login_required
def unsubscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.subscribers.remove(request.user)
    return redirect('news_list')

def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)

# def test_view(request):
#     logger.debug("Тестовый DEBUG лог")
#     logger.info("Тестовый INFO лог")
#     logger.warning("Тестовый WARNING лог")
#     logger.error("Тестовая ОШИБКА лог")
#     1 / 0  # вызов ZeroDivisionError
#     return HttpResponse("Done")
#
# @require_GET
# def trigger_error(request):
#     # Генерируем ошибку, которую перехватит Django
#     1 / 0
#     return HttpResponse("This won't be shown")