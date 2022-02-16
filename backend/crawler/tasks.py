import os, traceback

from .celery import app
from scrapy import spiderloader
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from billiard.context import Process
from datetime import datetime
from utils.shortcuts import get_env
from crawler.NLP_engine import NLP

settings = Settings()
os.environ["SCRAPY_SETTINGS_MODULE"] = "crawler.scrapy_app.settings"
settings_module_path = os.environ["SCRAPY_SETTINGS_MODULE"]
settings.setmodule(settings_module_path, priority="project")

spider_loader = spiderloader.SpiderLoader.from_settings(settings)

production_env = get_env("YG_ENV", "dev") == "production"


def crawling(spider_name, from_date, to_date):
    print('crawling start')
    process = CrawlerProcess(settings)
    process.crawl(spider_loader.load(spider_name), from_date=from_date, to_date=to_date)
    process.start()
    print('crawling finish')


def nlpanalysis(from_date, to_date):
    print('nlp analysis start')
    NLP.NLP_update(from_date, to_date)
    print('nlp analysis finish')


@app.task(name="schedule_task", bind=True)
def schedule_task(self, spider_name):
    current_time = datetime.now()
    from_date = to_date = current_time.strftime("%Y%m%d")
    print(from_date, to_date)
    try:
        crawl_process = Process(target=crawling, args=[spider_name, from_date, to_date])
        crawl_process.start()
        crawl_process.join()
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e)}

    try:
        nlp_process = Process(target=nlpanalysis, args=[from_date, to_date])
        nlp_process.start()
        nlp_process.join()
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e)}

    return {"success": True}
