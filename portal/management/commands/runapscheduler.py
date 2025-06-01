import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from portal.tasks import weekly_digest, delete_old_job_executions

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запускает APScheduler для периодических задач"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        # 1) еженедельный дайджест: понедельник, 08:00
        scheduler.add_job(
            weekly_digest,
            trigger=CronTrigger(day_of_week='mon', hour='08', minute='00'),
            id='weekly_digest',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача weekly_digest.")

        # 2) очистка истории: понедельник, 00:00
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week='mon', hour='00', minute='00'),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача delete_old_job_executions.")

        try:
            logger.info("Старт APScheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка APScheduler...")
            scheduler.shutdown()
            logger.info("Scheduler остановлен.")