import json

import scrapy
from crawler.scrapy_app.items import TwitterItem
from scrapy.loader import ItemLoader

import twint
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

geo_dict = {
    "North_America": "39.09988405413171,-94.57866878020425,2400km",
    "South_America": "-25.26125550803821,-57.57779557215821,3500km",
    "Southeast_Asia": "10.759904,106.682048,1800km",
    "Japan": "35.65864508541174,139.74547153338207,700km",
    "Europe": "47.804523, 13.042257,1200km",
    "India": "17.371338917502417,78.4803041351664,1000km",
    "Australia": "-28.00265437536671,134.39228939983974,2000km",
    "South_Africa": "-32.64648576305515,27.617846079254992,1100km",
    "Middle_East": "28.496720866936958,44.304230826320286,1600km",
    "Korea": "36.4842375131837,128.0233372268541,280km",
}


def write_json(path, data):
    if path[-5:] != ".json":
        path = path + ".json"
    with open(path, 'w', encoding="utf-8") as outfile:
        outfile.write(json.dumps(data, ensure_ascii=False))


def get_timedelta(period):
    # default is days=1
    timedelta = dt.timedelta(days=1)
    if period == "week":
        timedelta = dt.timedelta(weeks=1)
    elif period == "month":
        timedelta = relativedelta(months=1)
    elif period == "quarter":
        timedelta = relativedelta(months=3)
    elif period == "year":
        timedelta = relativedelta(years=1)
    return timedelta


def get_default_date():

    YYYY = dt.datetime.today().year  # 현재 연도 가져오기
    MM = dt.datetime.today().month  # 현재 월 가져오기
    DD = dt.datetime.today().day    # 현재 일 가져오기

    today_date = "{0:04d}-{1:02d}-{2:02d}".format(YYYY, MM, DD)
    today_datetime = dt.datetime.strptime(today_date, "%Y-%m-%d")
    yesterday_datetime = today_datetime - dt.timedelta(days=1)
    yesterday_date = dt.datetime.strftime(yesterday_datetime, "%Y-%m-%d")
    print(yesterday_date, " ~ ", today_date)
    return yesterday_date, today_date


class TwitterKeywordSpider(scrapy.Spider):
    name = 'twitter_keyword'
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'crawler.scrapy_app.middlewares.TwitterSpiderMiddleware': 800
        },
        'ITEM_PIPELINES': {
            'crawler.scrapy_app.pipelines.MongoDBPipelines': 400,
        }
    }

    def __init__(self, from_date='', to_date='', geo='', lang=''):
        self.config = twint.Config()
        self.set_custom(["id", "date", "username", "user_id",
                         "tweet", "language", "geo"])

        self.geoDict = geo_dict
        self.timedelta = get_timedelta("day")
        # if keywords != '':
        #     self.keywords = keywords.split(',')

        # 디폴트 값을 어제, 오늘로 설정
        self.from_date, self.to_date = get_default_date()

        if from_date != '':
            self.from_date = f'{from_date[:4]}-{from_date[4:6]}-{from_date[6:8]}'
        if to_date != '':
            self.to_date = f'{to_date[:4]}-{to_date[4:6]}-{to_date[6:8]}'
        self.geoList = [""]
        if geo != '':
            self.geoList = geo.split(',')
        self.lang = lang

    def set_custom(self, customList: list):
        self.config.Custom["tweet"] = customList
        print("Custom: ", self.config.Custom["tweet"])

    def start_requests(self):
        print("start_requests")
        start_url = 'http://quotes.toscrape.com/page/1/'
        yield scrapy.Request(url=start_url, callback=self.search)

    def search(self, response):

        self.config.Hide_output = False
        self.config.Popular_tweets = True

        # Language Filter (on)
        if self.lang != '':
            self.config.Lang = self.lang

        # Retweets Filter (off)
        self.config.Filter_retweets = True
        self.config.Retweets = False
        self.config.Native_retweets = False

        for geo in self.geoList:
            if geo != '':
                self.config.Geo = self.geoDict[geo]
                print(f"#### {geo} ####")

            print("spider keywords: ", self.keywords)
            for keyword in self.keywords:
                print(f"#### {keyword} ####")
                self.config.Search = keyword

                # date setting
                pivot = self.from_date
                date_since = datetime.strptime(self.from_date, '%Y-%m-%d')
                date_until = datetime.strptime(self.to_date, '%Y-%m-%d')
                date_pivot = date_since
                while True:
                    self.config.Limit = 2000
                    self.config.Store_object = True

                    self.config.Since = pivot
                    date_pivot = datetime.strptime(pivot, '%Y-%m-%d')

                    if date_pivot >= date_until:
                        # condition like do while statement
                        break
                    date_end = date_pivot + self.timedelta
                    end = date_end.strftime("%Y-%m-%d")
                    print("#### ", datetime.now(), "####")
                    print(
                        f"search for {keyword} between {self.config.Since} and {end}")
                    while True:
                        tweets = []
                        self.config.Store_object_tweets_list = tweets
                        if date_pivot >= datetime.strptime(end, '%Y-%m-%d'):
                            break
                        date_pivot = date_pivot + dt.timedelta(days=1)
                        pivot = datetime.strftime(date_pivot, '%Y-%m-%d')
                        self.config.Until = pivot

                        twint.run.Search(self.config)
                        print(
                            f"complete search for {keyword} between {self.config.Since} and {self.config.Until}")

                        for tweet in tweets:
                            loader = ItemLoader(
                                item=TwitterItem(), response=response)
                            loader.add_value('data_id', str(tweet.id))
                            loader.add_value(
                                'create_dt', tweet.datestamp + " " + tweet.timestamp)
                            loader.add_value('body', tweet.tweet)
                            loader.add_value('user_id', str(tweet.user_id))
                            loader.add_value('username', tweet.username)
                            loader.add_value('name', tweet.name)
                            loader.add_value('lang', tweet.lang)
                            loader.add_value('keyword', keyword)
                            loader.add_value('geo', geo)
                            loader.add_value('hashtags', tweet.hashtags)

                            yield loader.load_item()

                        print("Search Done!")

                        self.config.Since = pivot


class TwitterUserSpider(scrapy.Spider):
    name = 'twitter_user'
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'crawler.scrapy_app.middlewares.TwitterSpiderMiddleware': 800
        },
        'ITEM_PIPELINES': {
            'crawler.scrapy_app.pipelines.MongoDBPipelines': 400,
        }
    }

    def __init__(self, from_date='', to_date='', lang=''):
        self.config = twint.Config()
        self.set_custom(["id", "date", "username", "user_id",
                         "tweet", "language", "geo"])

        self.timedelta = get_timedelta("day")
        # if users != '':
        #     self.users = users.split(',')

        # 디폴트 값을 어제, 오늘로 설정
        self.from_date, self.to_date = get_default_date()

        if from_date != '':
            self.from_date = f'{from_date[:4]}-{from_date[4:6]}-{from_date[6:8]}'
        if to_date != '':
            self.to_date = f'{to_date[:4]}-{to_date[4:6]}-{to_date[6:8]}'

        self.lang = lang
        self.keyword = ''
        self.geo = ''

    def set_custom(self, customList: list):
        self.config.Custom["tweet"] = customList
        print("Custom: ", self.config.Custom["tweet"])

    def start_requests(self):
        print("start_requests")
        # fake url
        start_url = 'http://quotes.toscrape.com/page/1/'
        yield scrapy.Request(url=start_url, callback=self.search)

    def search(self, response):
        self.config.Hide_output = False
        self.config.Popular_tweets = True

        # Language Filter
        if self.lang != '':
            self.config.Lang = self.lang

        for username in self.users:
            print(f"#### {username} ####")
            self.config.Username = username

            # date setting
            pivot = self.from_date
            date_since = datetime.strptime(self.from_date, '%Y-%m-%d')
            date_until = datetime.strptime(self.to_date, '%Y-%m-%d')
            date_pivot = date_since
            while True:
                self.config.Store_object = True

                self.config.Since = pivot
                date_pivot = datetime.strptime(pivot, '%Y-%m-%d')

                if date_pivot >= date_until:
                    # condition like do while statement
                    break
                date_end = date_pivot + self.timedelta
                end = date_end.strftime("%Y-%m-%d")
                print("#### ", datetime.now(), "####")
                print(
                    f"search for {username} between {self.config.Since} and {end}")
                while True:
                    tweets = []
                    self.config.Store_object_tweets_list = tweets
                    if date_pivot >= datetime.strptime(end, '%Y-%m-%d'):
                        break
                    date_pivot = date_pivot + dt.timedelta(days=1)
                    pivot = datetime.strftime(date_pivot, '%Y-%m-%d')
                    self.config.Until = pivot

                    twint.run.Search(self.config)
                    print(
                        f"complete search for {username} between {self.config.Since} and {self.config.Until}")

                    for tweet in tweets:
                        loader = ItemLoader(
                            item=TwitterItem(), response=response)
                        loader.add_value('data_id', str(tweet.id))
                        loader.add_value(
                            'create_dt', tweet.datestamp + " " + tweet.timestamp)
                        loader.add_value('body', tweet.tweet)
                        loader.add_value('user_id', str(tweet.user_id))
                        loader.add_value('username', tweet.username)
                        loader.add_value('name', tweet.name)
                        loader.add_value('lang', tweet.lang)
                        loader.add_value('keyword', self.keyword)
                        loader.add_value('geo', self.geo)
                        loader.add_value('hashtags', tweet.hashtags)

                        yield loader.load_item()

                    print("Search Done!")

                    self.config.Since = pivot


class TwitterRTSpider(scrapy.Spider):
    name = 'twitter_user_rt'
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'crawler.scrapy_app.middlewares.TwitterSpiderMiddleware': 800
        },
        'ITEM_PIPELINES': {
            'crawler.scrapy_app.pipelines.MongoDBPipelines': 400,
        }
    }

    def __init__(self, from_date='', to_date='', lang=''):
        self.config = twint.Config()
        self.set_custom(["id", "conversation_id", "date",
                         "username", "user_id", "tweet", "language", "geo"])

        self.timedelta = get_timedelta("day")
        # 디폴트 값을 어제, 오늘로 설정
        self.from_date, self.to_date = get_default_date()

        # if users != '':
        #     self.users = users.split(',')

        if from_date != '':
            self.from_date = f'{from_date[:4]}-{from_date[4:6]}-{from_date[6:8]}'
        if to_date != '':
            self.to_date = f'{to_date[:4]}-{to_date[4:6]}-{to_date[6:8]}'

        self.lang = lang
        self.geo = ''
        self.keyword = ''

    def set_custom(self, customList: list):
        self.config.Custom["tweet"] = customList
        print("Custom: ", self.config.Custom["tweet"])

    def start_requests(self):
        print("start_requests")
        start_url = 'http://quotes.toscrape.com/page/1/'
        yield scrapy.Request(url=start_url, callback=self.search)

    def search(self, response):
        self.config.Hide_output = False
        self.config.Popular_tweets = True

        # Language Filter
        if self.lang != '':
            self.config.Lang = self.lang

        for username in self.users:
            print(f"#### {username} ####")
            self.config.Search = "@"+username

            # date setting
            pivot = self.from_date
            date_since = datetime.strptime(self.from_date, '%Y-%m-%d')
            date_until = datetime.strptime(self.to_date, '%Y-%m-%d')
            date_pivot = date_since
            while True:
                self.config.Store_object = True

                self.config.Since = pivot
                date_pivot = datetime.strptime(pivot, '%Y-%m-%d')

                if date_pivot >= date_until:
                    # condition like do while statement
                    break
                date_end = date_pivot + self.timedelta
                end = date_end.strftime("%Y-%m-%d")
                print("#### ", datetime.now(), "####")
                print(
                    f"search for {username} between {self.config.Since} and {end}")

                while True:
                    tweets = []
                    self.config.Store_object_tweets_list = tweets
                    if date_pivot >= datetime.strptime(end, '%Y-%m-%d'):
                        break
                    date_pivot = date_pivot + dt.timedelta(days=1)
                    pivot = datetime.strftime(date_pivot, '%Y-%m-%d')
                    self.config.Until = pivot

                    twint.run.Search(self.config)
                    print(
                        f"complete search for {username} between {self.config.Since} and {self.config.Until}")

                    for tweet in tweets:
                        loader = ItemLoader(
                            item=TwitterItem(), response=response)
                        loader.add_value('data_id', str(tweet.id))
                        loader.add_value(
                            'create_dt', tweet.datestamp + " " + tweet.timestamp)
                        loader.add_value('body', tweet.tweet)
                        loader.add_value('user_id', str(tweet.user_id))
                        loader.add_value('username', tweet.username)
                        loader.add_value('name', tweet.name)
                        loader.add_value('lang', tweet.lang)
                        loader.add_value('keyword', self.keyword)
                        loader.add_value('geo', self.geo)
                        loader.add_value('hashtags', tweet.hashtags)
                        loader.add_value(
                            'object_id', str(tweet.conversation_id))

                        yield loader.load_item()

                    print("Search Done!")

                    self.config.Since = pivot
