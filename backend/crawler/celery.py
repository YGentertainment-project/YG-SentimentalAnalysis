import os
from celery import Celery
from celery.schedules import crontab
from utils.shortcuts import get_env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yg.settings")

production_env = get_env("YG_ENV", "dev") == "production"
if production_env:
    app = Celery("crawler", backend="rpc://", broker="amqp://guest:guest@yg-as-rabbitmq:5672/")
else:
    app = Celery("crawler", backend="rpc://", broker="amqp://guest:guest@localhost:5672/")

app.config_from_object("django.conf:settings", "CELERY")
app.autodiscover_tasks()

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    timezone="Asia/Seoul",
    enable_utc=False,
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    worker_redirect_stdouts_level='INFO',
)

# 스케줄링 지정 부분
app.conf.beat_schedule = {
    "News-schedule-6am": {
        "task": "schedule_task",
        "schedule": crontab(minute=0, hour=6),
        "args": ["News"],
    },
    "News-schedule-6pm": {
        "task": "schedule_task",
        "schedule": crontab(minute=0, hour=18),
        "args": ["News"],
    }
    # 다른 크롤러에 대한 스케줄링을 추가하고 싶다면, [News]에 해당하는 부분을 다른 spider의 이름으로 변경하면 됩니다.
}