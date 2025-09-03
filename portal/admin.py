from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, Subscription
from modeltranslation.admin import TranslationAdmin

# Действие для обнуления рейтинга автора
def reset_author_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
reset_author_rating.short_description = 'Обнулить рейтинг авторов'

# Действие для обнуления рейтинга поста
def reset_post_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
reset_post_rating.short_description = 'Обнулить рейтинг постов'

# Действие для обнуления рейтинга комментария
def reset_comment_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
reset_comment_rating.short_description = 'Обнулить рейтинг комментариев'

# Действие для удаления всех подписчиков категории
def remove_category_subscribers(modeladmin, request, queryset):
    for category in queryset:
        category.subscribers.clear()
remove_category_subscribers.short_description = 'Удалить всех подписчиков категории'

# Inline для PostCategory
class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1
    verbose_name = "Категория"
    verbose_name_plural = "Категории"

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'user__email')
    actions = [reset_author_rating]

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', 'display_subscribers', 'subscribers_count')
    list_filter = ('name',)
    search_fields = ('name',)
    actions = [remove_category_subscribers]
    verbose_name_plural = 'Categories'

    def display_subscribers(self, obj):
        return ", ".join([user.username for user in obj.subscribers.all()])
    display_subscribers.short_description = 'Подписчики'

    def subscribers_count(self, obj):
        return obj.subscribers.count()
    subscribers_count.short_description = 'Количество подписчиков'

@admin.register(Post)
class PostAdmin(TranslationAdmin):
    inlines = [PostCategoryInline]
    list_display = ('title', 'post_type', 'author', 'created_at', 'rating', 'display_categories')
    list_filter = ('post_type', 'author', 'created_at', 'categories')  # Возвращаем стандартный фильтр
    search_fields = ('title', 'content', 'author__user__username')
    filter_horizontal = ('categories',)
    actions = [reset_post_rating]

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Категории'

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('post', 'category')
    list_filter = ('category',)
    search_fields = ('post__title', 'category__name')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'rating', 'text_preview')
    list_filter = ('post', 'user', 'created_at')
    search_fields = ('text', 'user__username', 'post__title')
    actions = [reset_comment_rating]

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('user__username', 'category__name')