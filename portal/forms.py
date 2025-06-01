from django import forms
from .models import Post, Category, Author, PostCategory
from allauth.account.forms import SignupForm
from django.utils import timezone


class NewsForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Категории*'
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not Author.objects.filter(user=self.user).exists():
            raise forms.ValidationError("Автор не найден! Обратитесь к администратору.")
        # Проверка авторизации
        if not self.user:
            raise forms.ValidationError("Пользователь не авторизован!")

        # Проверка категорий
        if not cleaned_data.get('categories'):
            raise forms.ValidationError("Выберите минимум одну категорию!")  # Новая проверка

        # Проверка лимита новостей
        author, _ = Author.objects.get_or_create(user=self.user)
        if Post.objects.filter(
                author=author,
                post_type='news',
                created_at__date=timezone.localtime(timezone.now()).date()
        ).count() >= 3:
            raise forms.ValidationError("Нельзя публиковать более 3 новостей в сутки!")

        return cleaned_data


class ArticleForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Категории',
        required = True
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        Author.objects.get_or_create(user=user)
        return user
