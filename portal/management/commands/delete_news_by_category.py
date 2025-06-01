from django.core.management.base import BaseCommand
from portal.models import Post, Category

class Command(BaseCommand):
    help = 'Удаляет все новости из указанной категории после подтверждения'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str, help='Имя категории, новости из которой нужно удалить')

    def handle(self, *args, **options):
        category_name = options['category']
        self.stdout.write(f'Вы действительно хотите удалить все новости в категории "{category_name}"? (yes/no)')
        answer = input()

        if answer.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Отменено'))
            return

        try:
            category = Category.objects.get(name=category_name)
            news_count = Post.objects.filter(post_type='news', categories=category).delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Успешно удалено {news_count} новостей из категории "{category.name}"'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория "{category_name}" не найдена'))