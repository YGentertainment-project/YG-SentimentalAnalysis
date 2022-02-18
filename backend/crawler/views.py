import os, requests, json

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .tasks import schedule_task

@csrf_exempt
@require_http_methods(["POST"])  # only post
def crawl(request):
    # 새로운 Task를 생성하는 POST 요청
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)  # body값 추출
        spider_name = body.get("name")
        from_date = body.get("from_date")
        to_date = body.get("to_date")
        task = schedule_task.apply_async(args=[spider_name, from_date, to_date])
        return JsonResponse({"task_id": task.id, "status": "started"})


@csrf_exempt
@require_http_methods(["PUT", "GET"])
def schedule(request):
    if request.method == "PUT":
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)  # body값 추출
        hour = body.get("hour")
        minute = body.get("minute")
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=hour,
            minute=minute,
            timezone="Asia/Seoul",
        )
        if PeriodicTask.objects.filter(name="News-schedule-6am").exists():
            task = PeriodicTask.objects.get(name="News-schedule-6am")
            task.enabled = True
            task.crontab = schedule
            task.save()
        return JsonResponse({"success": True})

    elif request.method == "GET":
        task_info = PeriodicTask.objects.filter(name="News-schedule-6am").values()
        crontab_id = task_info[0]["crontab_id"]
        crontab_info = CrontabSchedule.objects.filter(id=crontab_id).values()
        hour = crontab_info[0]["hour"]
        minute = crontab_info[0]["minute"]
        return JsonResponse({"hour": hour, "minute": minute})

