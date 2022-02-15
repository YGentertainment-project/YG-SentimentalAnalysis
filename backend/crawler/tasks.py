import os, traceback

from .celery import app
from scrapy import spiderloader
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from billiard.context import Process
from utils.shortcuts import get_env

settings = Settings()
os.environ["SCRAPY_SETTINGS_MODULE"] = "crawler.scrapy_app.settings"
settings_module_path = os.environ["SCRAPY_SETTINGS_MODULE"]
settings.setmodule(settings_module_path, priority="project")

spider_loader = spiderloader.SpiderLoader.from_settings(settings)

production_env = get_env("YG_ENV", "dev") == "production"


def crawling(spider_name,  from_date, to_date):
    print(spider_name, from_date, to_date)
    process = CrawlerProcess(settings)
    process.crawl(spider_loader.load(spider_name), from_date="2022-02-14", to_date="2022-02-15")
    process.start()


@app.task(name="schedule_task", bind=True)
def schedule_task(self, spider_name, from_date, to_date):
    try:
        process = Process(target=crawling, args=[spider_name, from_date, to_date])
        process.start()
        process.join()
    except Exception as e:
        traceback.print_exc()
    return {"success": True}
