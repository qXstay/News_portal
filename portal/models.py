from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        post_ratings = self.post_set.aggregate(models.Sum('rating'))['rating__sum'] or 0
        comment_ratings = self.user.comment_set.aggregate(models.Sum('rating'))['rating__sum'] or 0
        post_comment_ratings = Comment.objects.filter(post__author=self).aggregate(models.Sum('rating'))['rating__sum'] or 0

        self.rating = post_ratings * 3 + comment_ratings + post_comment_ratings
        self.save()

class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

class Post(models.Model):
    categories = models.ManyToManyField(Category, through='PostCategory', verbose_name=_('Categories'))
    NEWS = 'news'
    ARTICLE = 'article'
    objects = None
    POST_TYPES = [
        (NEWS, _("News")),
        (ARTICLE, _("Article")),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=7, choices=POST_TYPES, default=NEWS)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(_("Title"), max_length=255)
    content = models.TextField(_("Content"))
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def __str__(self):
        return self.title

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

