from django_filters import FilterSet, DateFilter, CharFilter
from .models import Post
import django.forms


class NewsFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название',
        widget=django.forms.TextInput(attrs={'class': 'form-control'})
    )

    author = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Автор',
        widget=django.forms.TextInput(attrs={'class': 'form-control'})
    )

    date = DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата (позже чем)',
        widget=django.forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Post
        fields = []