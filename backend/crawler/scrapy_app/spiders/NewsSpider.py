import re
import sys
import json
import scrapy
from datetime import datetime
from urllib import parse
from bs4 import element
from bs4 import BeautifulSoup as bs
from ..items import *

NAVER_SEARCH_LINK = 'https://search.naver.com/search.naver'
NAVER_NEWS_LINK = 'https://entertain.naver.com/read'
NAVER_REACTION_LINK = 'https://news.like.naver.com/v1/search/contents'

class NewsSpider(scrapy.Spider):
    name = 'News'
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'crawler.scrapy_app.middlewares.KeywordSQLMiddleware': 800
        }
    }

    def __init__(self, keywords='', from_date='', to_date='', **kwargs):
        super().__init__(**kwargs)
        self.keywords = []
        for keyword in keywords.split(','):
            if keyword != '' :
                self.keywords.append(keyword)
        
        self.date_filter = False
        if (from_date == '') ^ (to_date == ''):
            print('Error, from_date and to_date must insert together')
            sys.exit(1)
        elif from_date != '':
            self.date_filter = True
            self.from_date = from_date
            self.to_date = to_date

    def start_requests(self):
        query = {
            'start': 1,
            'sort': 1,
            'where': 'news'
        }
        if self.date_filter:
            query['nso'] = f'p:from{self.from_date}to{self.to_date}'
        for keyword in self.keywords:
            query['query'] = f'\"{keyword}\"'
            query_str = parse.urlencode(query)
            yield scrapy.Request(
                f'{NAVER_SEARCH_LINK}?{query_str}',
                self.parse_news_list,
                meta={'keyword': keyword, 'start': 1}
            )

    def url_checker(self, url):
        parsed_url = parse.urlparse(url)
        parsed_query = dict(parse.parse_qsl(parsed_url.query))
        if 'oid' in parsed_query and 'aid' in parsed_query:
            return True, (parsed_query['oid'], parsed_query['aid'])
        else:
            return False, 'Not NaverNews'

    def parse_news_list(self, response):
        soup = bs(response.body, 'html.parser')
        news_items = soup.select('div.news_area')
        for news in news_items:
            naver_news_link = news.select_one('div.info_group > a.info:not(.press)')
            if naver_news_link is None:
                continue
            link = naver_news_link['href']
            flag, link = self.url_checker(link)
            snippet_text = news.select_one('a.dsc_txt_wrap').text
            if flag:
                yield scrapy.Request(
                    f'{NAVER_NEWS_LINK}?oid={link[0]}&aid={link[1]}',
                    self.parse_news_article,
                    meta={
                        'keyword': response.meta['keyword'],
                        'snippet': snippet_text
                    }
                )
        next_btn = soup.select_one('.btn_next')
        if next_btn is not None and next_btn['aria-disabled'] is not None and next_btn['aria-disabled'] == 'false':
            query = {
                'start': response.meta['start'] + 10,
                'sort': 1,
                'where': 'news'
            }
            if self.date_filter:
                query['nso'] = f'p:from{self.from_date}to{self.to_date}'
                query['ds'] = f'{self.from_date[:4]}.{self.from_date[4:6]}.{self.from_date[6:8]}'
                query['de'] = f'{self.to_date[:4]}.{self.to_date[4:6]}.{self.to_date[6:8]}'
            query['query'] = f'\"{response.meta["keyword"]}\"'
            query_str = parse.urlencode(query)
            yield scrapy.Request(
                f'{NAVER_SEARCH_LINK}?{query_str}',
                self.parse_news_list,
                meta={'keyword': response.meta["keyword"], 'start': response.meta['start'] + 10},
                dont_filter=True
            )
    
    def korean_date_to_iso8601(self, korean_date):
        # ex 2021.12.21 오후 1:36
        date_arr = korean_date.split()
        date = datetime.strptime(date_arr[0], '%Y.%m.%d.')
        time = datetime.strptime(date_arr[2], '%I:%M')
        if date_arr[1] == '오후':
            date = date.replace(hour=time.hour + 12, minute=time.minute)
        else:
            date = date.replace(hour=time.hour, minute=time.minute)
        return date
    
    def parse_news_article(self, response):
        soup = bs(response.body, 'html.parser')
        if 'entertain' in response.url:
            title = soup.select_one('h2.end_tit').text
            body = soup.select_one('#articeBody')
        else:
            title = soup.select_one('#articleTitle').text
            body = soup.select_one('#articleBodyContents')
        if body is None:
            body = ''
        else:
            body_text = '\n'.join(body.findAll(text=True, recursive=False))
            for child in body.children:
                if type(child) == element.Tag:
                    body_text += '\n'.join(child.findAll(text=True, recursive=False)) + '\n'
            body = ' '.join(body_text.split('\n')[:-1])
            body = re.sub('(\ |\t)+', ' ', body.strip())
        title = ' '.join(title.split('\n'))
        title = re.sub('(\ |\t)+', ' ', title.strip())
        press = soup.select_one('.press_logo > img')['alt']
        reporter = soup.select_one('.journalistcard_summary_name')
        if reporter is not None:
            reporter = reporter.text.replace('기자', '').strip()
        else: 
            reporter = re.search('[^가-힣][가-힣]{2,4} 기자[^가-힣]', body)
            if reporter is not None:
                reporter = reporter[0][1:-4]
        # 기자 이름 및 언론사 제거 (ex. [서울신문=홍길동 기자])
        body = re.sub('^\[[^\]]*]|^\([^\)]*\)', '', body).strip()
        # 기자 이름 제거
        body = re.sub('([^가-힣]|)[가-힣]{2,4}( |)(인턴|인턴| )( |)기자[^가-힣](= |)', '', body).strip()
        # 기자 이메일 제거
        body = re.sub(
            "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])",
            '', body).strip()
        pub_date = soup.select_one('div.article_info > span > em').text.strip()
        pub_date = self.korean_date_to_iso8601(pub_date)
        _, (oid, aid) = self.url_checker(response.url)
        item = NewsItem(
            _id=f'{oid}_{aid}',
            data_id=f'{oid}_{aid}',
            press=press,
            reporter=reporter,
            title=title,
            body=body,
            snippet=response.meta['snippet'],
            url=response.url,
            keyword=self.keyword_groups[response.meta['keyword']],
            create_dt=pub_date
        )
        data_cid = soup.select_one('._reactionModule')['data-cid']
        query = {
            'callback': 'A',
            'q': f'ENTERTAIN[{data_cid}]'
        }
        query_str = parse.urlencode(query)
        yield scrapy.Request(
            f'{NAVER_REACTION_LINK}?{query_str}',
            self.get_article_reaction,
            meta={'item': item}
        )
    
    def get_article_reaction(self, response):
        data = json.loads(response.body[6:-2])
        reactions = {}
        for reaction in data['contents'][0]['reactions']:
            reactions[reaction['reactionType']] = reaction['count']
        item = response.meta['item']
        item['reaction'] = reactions
        item['reaction_sum'] = sum(reactions.values())
        yield item
