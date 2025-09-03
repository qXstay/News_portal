from django.core.management.base import BaseCommand
from portal.models import Post
from googletrans import Translator


class Command(BaseCommand):
    help = 'Translates first five news items to English'

    def handle(self, *args, **options):
        # Берем первые 5 новостей
        news = Post.objects.filter(post_type='news').order_by('-created_at')[:5]
        translator = Translator()

        for news_item in news:
            # Переводим только если английская версия пуста
            if not news_item.title_en or not news_item.content_en:
                try:
                    # Переводим заголовок
                    if not news_item.title_en:
                        news_item.title_en = translator.translate(news_item.title, dest='en').text

                    # Переводим содержание
                    if not news_item.content_en:
                        # Для длинного контента разбиваем на части
                        content_parts = news_item.content.split('. ')
                        translated_parts = []
                        for part in content_parts:
                            if part:  # Пропускаем пустые части
                                translated = translator.translate(part, dest='en').text
                                translated_parts.append(translated)
                        news_item.content_en = '. '.join(translated_parts)

                    news_item.save()
                    self.stdout.write(self.style.SUCCESS(f'Translated news: {news_item.title}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error translating news {news_item.id}: {str(e)}'))