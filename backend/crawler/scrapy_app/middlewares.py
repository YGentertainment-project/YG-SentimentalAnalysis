# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from os import spawnl
from scrapy import signals
import pymysql
from .apikey import *
import sshtunnel

class NewsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NewsDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if spider.name == 'UK_guardian' :
            remain_quota = response.headers.getlist('X-Ratelimit-Remaining-Day')
            if len(remain_quota) > 0 :
                print('The Guardian: ', remain_quota[0].decode('utf-8'))
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class IGSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        
    def spider_closed(self, spider):
        print(spider.name)
        print(spider.cookie)
        spider.driver.close()
        
class TwitterSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
    
    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r
            
    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        try:
            conn = pymysql.connect(
                user=SQL_USER,
                passwd=SQL_PW,
                host=SQL_HOST,
                port=SQL_PORT,
                db=SQL_DB
            )
            cursor = conn.cursor(pymysql.cursors.DictCursor)
        except:
            print('ERROR: DB connection failed')
        print(spider.name)
        select_arg_platform = [1] #temp platform_id=1: twitter
        select_sql_keyword = """select id, artist_id, platform_id, keyword from collect_target_keyword where platform_id=%s"""
        
        select_sql_channel = """select id, artist_id, platform_id, target_url, channel, channel_name from collect_target where platform_id=%s"""
        if spider.name in ["twitter_keyword"]:
            cursor.execute(select_sql_keyword, select_arg_platform)
            rows = cursor.fetchall()
            print()
            keywords = []
            try:
                for i in range(len(rows)):
                    fetch_keyword = rows[i]["keyword"]
                    keywords.append(fetch_keyword)
            except Exception as e:
                print(e)
                
            spider.keywords=keywords
            print("spider.keywords: ", spider.keywords)
        elif spider.name in ["twitter_user", "twitter_user_rt"] :
            cursor.execute(select_sql_channel, select_arg_platform)
            rows = cursor.fetchall()
            print()
            channel_names = []
            try:
                for i in range(len(rows)):
                    print(type(rows[i]), rows[i])
                    fetch_channel_name = rows[i]["channel_name"]
                    
                    print(fetch_channel_name)
                    channel_names.append(fetch_channel_name)
            except Exception as e:
                print(e)
            spider.users=channel_names
            print("spider.users: ", spider.users)    
        
    def spider_closed(self, spider):
        print(spider.name)


class KeywordSQLMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
    
    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r
            
    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        
        spider.logger.info(f'Set Connection to Database: Start')
        if SSH_MARIA_ENABLE:
            self.tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_HOST, SSH_PORT),
                ssh_username=SSH_USER,
                ssh_password=SSH_PSWD,
                remote_bind_address=('127.0.0.1', SQL_PORT),
                local_bind_address=('0.0.0.0', SQL_PORT)
            )
            self.tunnel.start()
            conn = pymysql.connect(
                user=SQL_USER,
                passwd=SQL_PW,
                host='127.0.0.1',
                port=SQL_PORT,
                db=SQL_DB
            )
        else:
            conn = pymysql.connect(
                user=SQL_USER,
                passwd=SQL_PW,
                host=SQL_HOST,
                port=SQL_PORT,
                db=SQL_DB
            )
        
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
        except:
            spider.logger.error(f'Set Connection to Database: Fail')
        spider.logger.info(f'Set Connection to Database: Success')
        
        if spider.name == 'News':
            select_sql_keyword = '''SELECT B.keyword 
                                    FROM collect_target_keyword_group A, collect_target_keyword B
                                    WHERE news_platform = 1 AND A.id = B.group_id'''
        else:
            select_sql_keyword = '''SELECT B.keyword 
                                    FROM collect_target_keyword_group A, collect_target_keyword B
                                    WHERE sns_platform = 1 AND A.id = B.group_id'''
        cursor.execute(select_sql_keyword)
        rows = cursor.fetchall()
        spider.keywords = [row['keyword'] for row in rows]
        spider.logger.info(f'Keyword From Database: {spider.keywords}')
        
    def spider_closed(self, spider):
        print(spider.name)
