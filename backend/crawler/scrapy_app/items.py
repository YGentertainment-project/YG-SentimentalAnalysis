# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem
from crawler.models import Youtube, News, IG, FB, Twitter


class YoutubeItem(DjangoItem):
    django_model = Youtube


class NewsItem(DjangoItem):
    django_model = News


class IGItem(DjangoItem):
    django_model = IG


class FBItem(DjangoItem):
    django_models = FB


class TwitterItem(DjangoItem):
    django_models = Twitter
