from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from celery import shared_task
from .models import Category, Post
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def weekly_digest():
    """
    Раз в неделю шлём список новых новостей и статей за последние 7 дней.
    """
    logger.info("[weekly_digest] запуск задачи")
    week_ago = timezone.now() - timezone.timedelta(days=7)

    try:
        domain = Site.objects.get_current().domain
    except Site.DoesNotExist:
        domain = "example.com"  # Fallback domain

    for category in Category.objects.all():
        new_posts = Post.objects.filter(
            created_at__gte=week_ago,
            categories=category
        )

        if not new_posts.exists():
            logger.info(f"[weekly_digest] в категории {category.name} новых постов нет")
            continue

        logger.info(f"[weekly_digest] сформировано {new_posts.count()} постов для категории {category.name}")

        for user in category.subscribers.all():
            if not user.email:
                continue

            try:
                html = render_to_string('portal/email/weekly_digest.html', {
                    'user': user,
                    'category': category,
                    'posts': new_posts,
                    'site_domain': domain,
                })

                msg = EmailMultiAlternatives(
                    subject=f'Новые публикации в «{category.name}» за неделю',
                    body='У вас есть новые публикации — включите HTML-почту',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html, 'text/html')
                msg.send()
                logger.info(f"[weekly_digest] письмо отправлено {user.email}")
            except Exception as e:
                logger.error(f"[weekly_digest] ошибка отправки {user.email}: {e}")


@shared_task
def delete_old_job_executions(max_age=604_800):
    """
    Удаляем записи о выполнении задач старше max_age секунд.
    """
    try:
        DjangoJobExecution.objects.delete_old_job_executions(max_age)
        logger.info(f"Удалены старые задачи старше {max_age} секунд")
    except Exception as e:
        logger.error(f"Ошибка при удалении старых задач: {e}")


@shared_task
def new_post_notification(post_id):
    """
    Асинхронная отправка писем подписчикам при создании новости.
    """
    try:
        post = Post.objects.get(pk=post_id)
        if post.post_type != 'news':  # Отправляем только для новостей
            logger.info(f"Пропуск отправки: пост {post_id} не является новостью")
            return

        try:
            domain = Site.objects.get_current().domain
        except Site.DoesNotExist:
            domain = "example.com"  # Fallback domain

        subscribers = set()
        for cat in post.categories.all():
            subscribers.update(cat.subscribers.all())

        if not subscribers:
            logger.info(f"Для поста {post_id} нет подписчиков")
            return

        for user in subscribers:
            if not user.email or user.email == settings.DEFAULT_FROM_EMAIL:
                continue

            try:
                clean_domain = domain.replace('/ru', '').replace('/en', '')

                html = render_to_string('portal/email/new_post_notification.html', {
                    'post': post,
                    'user': user,
                    'preview': post.content[:50] + '...',
                    'domain': clean_domain
                })

                msg = EmailMultiAlternatives(
                    subject=post.title,
                    body=post.content[:50] + '...',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html, 'text/html')
                msg.send()
                logger.info(f"Уведомление отправлено {user.email} для поста {post_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки {user.email}: {e}")

    except Post.DoesNotExist:
        logger.error(f"Пост {post_id} не найден")
    except Exception as e:
        logger.error(f"Ошибка в задаче отправки уведомлений: {e}")