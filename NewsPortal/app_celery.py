import os
# noinspection PyUnresolvedReferences
from celery import Celery
# noinspection PyUnresolvedReferences
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')
app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # еженедельный дайджест каждый понедельник в 8:00
    'weekly_digest': {
        'task': 'portal.tasks.weekly_digest',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник
    },
    'cleanup_jobs': {
        'task': 'portal.tasks.delete_old_job_executions',
        'schedule': crontab(hour=0, minute=0),  # Ежедневно в полночь
    },
}