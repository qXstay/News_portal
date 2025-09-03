import logging
from allauth.account.signals import email_confirmed
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.cache import cache
from .models import Post, Author
from .tasks import new_post_notification
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

@receiver(email_confirmed)
def send_welcome_after_confirm(request, email_address, **kwargs):
    try:
        user = email_address.user
        html = render_to_string('account/email/welcome_after_confirm.html', {'user': user})
        msg = EmailMultiAlternatives(
            subject=f'Добро пожаловать, {user.username}!',
            body=f'Привет, {user.username}!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        logger.info(f"Приветственное письмо отправлено {user.email}")
    except Exception as e:
        logger.error(f"Ошибка отправки приветственного письма: {e}")

@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_category_add(sender, instance, action, **kwargs):
    """
    Сигнал m2m_changed на добавление категорий к посту.
    Вызывается после form.save_m2m(), когда категории уже привязаны.
    """
    # Нас интересует только окончательное добавление новости
    if action == 'post_add' and instance.post_type == 'news':
        logger.info(f"Запуск задачи отправки уведомлений для поста ID={instance.id}")
        new_post_notification.delay(instance.id)


@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    """
    При создании нового пользователя:
    - автоматически в группу common
    - создаём запись Author
    """
    if not created:
        return

    try:
        # Добавление в группу common
        common_group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)

        # Создание автора
        Author.objects.get_or_create(user=instance)

        logger.info(f"Пользователь {instance.username} добавлен в группу common и создан как Author")
    except Exception as e:
        logger.error(f"Ошибка при инициализации пользователя: {e}")

@receiver(post_save, sender=Post)
def invalidate_cache_on_save(sender, instance, created, **kwargs):
    """
    Очистка кэша при создании или обновлении поста
    """
    try:
        if instance.post_type == 'news':
            cache.delete('news_list')
        if instance.post_type == 'article':
            cache.delete('article_list')
        cache.delete(f'post_{instance.id}')
        logger.debug(f"Кэш очищен для поста {instance.id}")
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")

@receiver(post_delete, sender=Post)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """
    Очистка кэша при удалении поста
    """
    try:
        if instance.post_type == 'news':
            cache.delete('news_list')
        if instance.post_type == 'article':
            cache.delete('article_list')
        cache.delete(f'post_{instance.id}')
        logger.debug(f"Кэш очищен для удаленного поста {instance.id}")
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")

@receiver(post_save, sender=Post)
def test_signal(sender, instance, created, **kwargs):
    if created:
        logger.info(f"TEST SIGNAL: Post created - ID {instance.id}, Type {instance.post_type}")
        logger.error(f"TEST ERROR LOG: Post {instance.id}")

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)