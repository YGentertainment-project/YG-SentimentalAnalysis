import os, requests, json

from django.shortcuts import render
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