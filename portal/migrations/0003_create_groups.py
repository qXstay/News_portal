from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="common")
    Group.objects.get_or_create(name="authors")

class Migration(migrations.Migration):
    dependencies = [
        # Указываем последнюю существующую миграцию (ваш 0002_create_subscription)
        ("portal", "0002_create_subscription"),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]