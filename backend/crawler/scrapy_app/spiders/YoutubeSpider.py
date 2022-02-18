from datetime import datetime, timedelta
import re
import sys
import json
import scrapy
from urllib import parse
from ..apikey import YT_APIKEY
from ..items import YoutubeItem

YT_API_LINK = 'https://www.googleapis.com/youtube/v3/'

class YoutubeSpider(scrapy.Spider):
    name = 'Youtube'
    allowed_domains = ['youtube.com', 'googleapis.com']

    def __init__(self, 
                 channel_ids='', keywords='', 
                 from_date='', to_date='', 
                 crawling_mode='Comment',
                 **kwargs):
        super().__init__(**kwargs)
        self.ids = []
        for id in channel_ids.split(','):
            if id != '' :
                self.ids.append({'type':'channel_id', 'id': id})
        for keyword in keywords.split(','):
            if keyword != '' :
                self.ids.append({'type':'keyword', 'id': keyword})
        
        self.date_filter = False
        if (from_date == '') ^ (to_date == ''):
            print('Error, from_date and to_date must insert together')
            sys.exit(1)
        elif from_date != '':
            self.date_filter = True
            self.from_date = datetime.strptime(from_date, '%Y%m%d')
            self.to_date = datetime.strptime(to_date, '%Y%m%d').replace(hour=23, minute=59, second=59)
        crawling_mode_list = ['Comment', 'Subcomment']
        if crawling_mode not in crawling_mode_list:
            print(f'Crawling_mode must be [{crawling_mode_list}]')
            sys.exit(1)
        else:
            self.crawling_mode = crawling_mode

    def start_requests(self):
        for id in self.ids :
            query = {
                'key': YT_APIKEY,
                'part': 'snippet',
                'maxResults': 100
            }
            #Channel ID
            if id['type'] == 'channel_id' :
                query['part'] = 'snippet,replies, id'
                query['allThreadsRelatedToChannelId'] = id['id']
                query_str = parse.urlencode(query)
                yield scrapy.Request(
                        f'{YT_API_LINK}commentThreads?{query_str}', 
                        self.parse_video,
                        meta={'type': 'Channel','id': id['id']}
                    )
            #Keyword
            if id['type'] == 'keyword' :
                query['part'] = 'snippet, id'
                query['type'] = 'video'
                query['q'] = id['id']
                query_str = parse.urlencode(query)
                yield scrapy.Request(
                        f'{YT_API_LINK}search?{query_str}', 
                        self.get_search_result,
                        meta={'id': id['id']}
                    )

    def get_meta_channel(self, response) :
        data = json.loads(response.body)
        data = data['items'][0]
        doc = YoutubeItem()
        doc['data_id'] = data['id']
        doc['title'] = data['snippet']['title']
        doc['desc'] = data['snippet']['description']
        doc['view'] = data['statistics']['viewCount']
        doc['subs'] = data['statistics']['subscriberCount']
        doc['video'] = data['statistics']['videoCount']
        # yield doc
        query = {
            'key': YT_APIKEY,
            'part': 'snippet',
        }
        query['type'] = 'video'
        query['channelId'] = response.meta['id']
        query_str = parse.urlencode(query)
        yield scrapy.Request(
                f'{YT_API_LINK}search?{query_str}',
                self.get_search_result,
                meta={'Channel':doc}
            )
    
    def get_meta_video(self, response) :
        data = json.loads(response.body)
        meta = response.meta
        data = data['items'][0]
        doc = YoutubeItem()
        date = data['snippet']['publishedAt']
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        doc['data_id'] = data['id']
        doc['channelId'] = data['snippet']['channelId']
        doc['title'] = data['snippet']['title']
        doc['desc'] = data['snippet']['description']
        doc['create_dt'] = date + timedelta(hours=9)
        doc['view'] = data['statistics']['viewCount']
        doc['like'] = data['statistics']['likeCount']
        meta['Video'] = doc
        
        if self.from_date <= doc['create_dt'] and doc['create_dt'] <= self.to_date:
            yield doc
    
        if 'type' in response.meta and response.meta['type'] == 'Video' :
            query = {
                'key': YT_APIKEY,
                'part': 'snippet, statistics',
                'id': data['snippet']['channelId']
            }
            query_str = parse.urlencode(query)
            yield scrapy.Request(
                    f'{YT_API_LINK}channels?{query_str}', 
                    self.get_meta_channel,
                    meta={'type': 'Video','id': response.meta['id'], 'video_item':doc},
                    dont_filter=True
                    )
        else :
            query = {
                'key': YT_APIKEY,
                'part': 'snippet, id, replies',
                'maxResults': 100,
                'videoId': data['id']
            }
            query_str = parse.urlencode(query)
            yield scrapy.Request(f'{YT_API_LINK}commentThreads?{query_str}', self.parse_video, meta=meta)

    def get_search_result(self, response):
        data = json.loads(response.body)
        for video in data['items'] :
            query = {
                'key': YT_APIKEY,
                'part': 'snippet,statistics',
                'id': video['id']['videoId']
            }
            query_str = parse.urlencode(query)
            yield scrapy.Request(
                    f'{YT_API_LINK}videos?{query_str}', 
                    self.get_meta_video, 
                    meta=response.meta
                )
        
        if 'nextPageToken' in data :
            parsed_query = dict(parse.parse_qsl(response.url[response.url.find('?') + 1:]))
            parsed_query['pageToken'] = data['nextPageToken']
            query_str = parse.urlencode(parsed_query)
            yield scrapy.Request(
                    f'{YT_API_LINK}search?{query_str}', 
                    self.get_search_result,
                    meta=response.meta
                )

    def parse_video(self, response) :
        data = json.loads(response.body)
        next_page_flag = True
        for comment in data['items'] :
            top_comment = comment['snippet']['topLevelComment']
            doc = YoutubeItem()
            date = top_comment['snippet']['publishedAt']
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            doc['data_id']   = top_comment['id']
            doc['channelId'] = top_comment['snippet']['channelId']
            doc['videoId']   = top_comment['snippet']['videoId']
            doc['body']      = top_comment['snippet']['textOriginal']
            doc['create_dt'] = date + timedelta(hours=9)
            doc['like']      = top_comment['snippet']['likeCount']
            if self.from_date <= doc['create_dt'] and doc['create_dt'] <= self.to_date and self.crawling_mode == 'Comment':
                yield doc
            elif doc['create_dt'] < self.from_date:
                next_page_flag = False
                break
            # if comment['snippet']['totalReplyCount'] > 0 :
            #     for repl in comment['replies']['comments'] :
            #         doc = YoutubeCommentItem()
            #         doc['commentId'] = repl['id']
            #         doc['videoId']   = repl['snippet']['videoId']
            #         doc['body']      = repl['snippet']['textDisplay']
            #         doc['datetime']  = repl['snippet']['publishedAt']
            #         doc['like']      = repl['snippet']['likeCount']
            #         yield doc
        
        if 'nextPageToken' in data and (next_page_flag or self.crawling_mode == 'Subcomment'):
            parsed_query = dict(parse.parse_qsl(response.url[response.url.find('?') + 1:]))
            parsed_query['pageToken'] = data['nextPageToken']
            query_str = parse.urlencode(parsed_query)
            yield scrapy.Request(f'{YT_API_LINK}commentThreads?{query_str}', self.parse_video, meta=response.meta)