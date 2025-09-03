from django import forms
from .models import Post, Category
from allauth.account.forms import SignupForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging


logger = logging.getLogger(__name__)


class NewsForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Categories*")
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        labels = {
            'title': _("Title"),
            'content': _("Content"),
            'categories': _("Categories")
        }
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': _("Enter post content here")})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Проверяем, что пользователь является автором
        from .models import Author

        # Если автор не существует - показываем ошибку
        if not Author.objects.filter(user=self.user).exists():
            raise forms.ValidationError(
                _("You are not an author. Please become an author first.")
            )

        # Получаем автора
        author = Author.objects.get(user=self.user)

        if not cleaned_data.get('categories'):
            raise forms.ValidationError(_("Select at least one category!"))

        # Проверка лимита публикаций
        today = timezone.localtime(timezone.now()).date()
        if Post.objects.filter(
                author=author,
                post_type='news',
                created_at__date=today
        ).count() >= 3:
            raise forms.ValidationError(_("You cannot publish more than 3 news per day!"))

        return cleaned_data


class ArticleForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_("Categories"),
        required=True
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        labels = {
            'title': _("Title"),
            'content': _("Content"),
            'categories': _("Categories")
        }


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        from .models import Author  # Локальный импорт для избежания циклических зависимостей
        Author.objects.get_or_create(user=user)
        return user