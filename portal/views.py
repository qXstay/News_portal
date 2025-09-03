from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Author, Category
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import NewsForm, ArticleForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .filters import NewsFilter
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import logging
from .mixins import EmailVerifiedRequiredMixin
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.utils import translation
from django.shortcuts import redirect
import pytz
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import PostSerializer
from django.utils import timezone


logger = logging.getLogger(__name__)
logger = logging.getLogger('django')

def authors_only(user):
    return user.groups.filter(name='authors').exists()

# Временно отключаем кэширование для тестирования
# @cache_page(60 * 5)
def news_list(request):
    # Активируем язык пользователя
    user_language = request.LANGUAGE_CODE
    translation.activate(user_language)

    news = Post.objects.filter(post_type='news').order_by('-created_at')

    # Для первых 5 новостей принудительно используем переведенные версии
    for news_item in news[:5]:
        if user_language == 'en':
            # Используем английскую версию, если она существует
            news_item.title = news_item.title_en or news_item.title
            news_item.content = news_item.content_en or news_item.content

    paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'portal/news_list.html', {
        'page_obj': page_obj,
        'page_title': _("News List")
    })

# @cache_page(60 * 5)
def article_list(request):
    articles = Post.objects.filter(post_type='article').order_by('-created_at')
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'portal/article_list.html', {
        'page_obj': page_obj,
        'page_title': _("Article List")
    })

# @cache_page(60 * 5)
def news_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Активируем язык пользователя
    user_language = request.LANGUAGE_CODE
    translation.activate(user_language)

    # Если это одна из первых 5 новостей и язык английский
    if user_language == 'en':
        # Проверяем, входит ли новость в первые 5
        first_five_ids = Post.objects.filter(post_type='news').order_by('-created_at').values_list('id', flat=True)[:5]

        if post.id in first_five_ids:
            # Используем английскую версию, если она существует
            post.title = post.title_en or post.title
            post.content = post.content_en or post.content

    return render(request, 'portal/news_detail.html', {'post': post})

# @cache_page(60)
def home(request):
    lang_code = request.COOKIES.get('django_language')
    if lang_code:
        translation.activate(lang_code)
    return render(request, 'portal/index.html', {'title': _('Home Page')})

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
        context['form_title'] = _("Create News Article")
        return context

class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = NewsForm
    template_name = 'portal/post_edit.html'
    success_url = reverse_lazy('news_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
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

    # Добавляем пользователя в группу authors
    if not user.groups.filter(name='authors').exists():
        user.groups.add(authors_group)

        # Создаём запись Author
        from .models import Author
        Author.objects.get_or_create(user=user)

        messages.success(request, _("You are now an author!"))
    else:
        messages.info(request, _("You are already an author"))

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
    return render(request, '403.html', {'error_message': _("You don't have permission to perform this action")}, status=403)

def set_timezone(request):
    if request.method == 'POST':
        tz = request.POST.get('timezone')
        if tz:
            request.session['django_timezone'] = tz
            messages.success(request, _("Timezone changed to") + f" {tz}")
    return redirect(request.META.get('HTTP_REFERER', '/'))


class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.filter(post_type='news').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # Проверка лимита новостей
        today = timezone.localtime(timezone.now()).date()
        author = request.user.author

        if Post.objects.filter(
                author=author,
                post_type='news',
                created_at__date=today
        ).count() >= 3:
            return Response(
                {"error": _("You cannot publish more than 3 news per day!")},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        author = self.request.user.author
        serializer.save(author=author, post_type='news')


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.filter(post_type='article').order_by('-created_at')

    def perform_create(self, serializer):
        author = self.request.user.author
        serializer.save(author=author, post_type='article')