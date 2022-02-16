import re
import sys
import scrapy
import logging

from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from ..apikey import CHROMEDRIVER_PATH, CROWDTANGLE_EMAIL, CROWDTANGLE_PASSWORD, CROWDTANGLE_FB_LINK
from ..items import FBItem

class FBSpider(scrapy.Spider):
    name = 'Facebook'
    start_urls = ['https://apps.crowdtangle.com/']
    custom_settings = {
        'SPIDER_MIDDLEWARES': {
            'crawler.scrapy_app.middlewares.IGSpiderMiddleware': 100
        }
    }
    post_per_day=100
    channels={
        "(여자)아이들":"G.I.DLE.CUBE",
        "뉴이스트":"pledisnuest",
        "레드벨벳":"RedVelvet",
        "마마무":"RBW.MAMAMOO",
        "몬스타엑스":"OfficialMonstaX",
        "방탄소년단":"bangtan.official",
        "BLACKPINK":"BLACKPINKOFFICIAL",
        "BIGBANG":"BIGBANG",
        "BIGBANG 지드래곤":"gdragon",
        "샤이니":"shinee",
        "세븐틴":"seventeennews",
        "슈퍼주니어":"superjunior",
        "스트레이키즈":"JYPEStrayKids",
        "아스트로":"offclASTRO",
        "에스파":"aespa.official",
        "WINNER":"OfficialYGWINNER",
        "크래비티":"OfficialCRAVITY",
        "트와이스":"JYPETWICE",
        "AB6IX":"AB6IX",
        "에이티즈":"ATEEZofficial",
        "엔하이픈":"officialENHYPEN",
        "EXO":"weareoneEXO",
        "iKON":"OfficialYGiKON",
        "ITZY":"OfficialItzy",
        "NCT":"NCT.smtown",
        "NCT 127":"NCT127.smtown",
        "NCT DREAM":"NCTDREAM.smtown",
        "더보이즈":"officialTHEBOYZ",
        "TREASURE":"OfficialTreasure",
        "TXT":"TXT.bighit",
        "WayV":"WayV.official",
        "청하":"ChungHa.MNHent",
        "선미":"officialsunmi",
        "전소미":"somsomi.official",
        "AKMU":"officialAKMU",
        "아이유":"iu.loen",
        "헤이즈":"HeizeOfficial",
        "소녀시대":"girlsgeneration",
        "이하이":"OfficialLEEHI",
        "젝스키스":"OfficialSECHSKIES",
        "볼빨간사춘기":"BOL4.Official",
        "현아":"hyunaofficial.pnation",
        "비투비":"BTOBofficial",
        "SF9":"SF9official",
        "스테이씨":"STAYC",
        "오마이걸":"official.ohmygirl",
        "위클리":"WeeeklyOfficial"
    }
    keywords=[
        '블랙핑크',
        '위너'
    ]

    def __init__(self, from_date='', to_date='', channel_mode='True', keyword_mode='False', **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1280,720')
        options.add_argument('loglevel=3')
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
        self.driver.implicitly_wait(3)
        selenium_logger.setLevel(logging.CRITICAL)
        self.crowdtangle_login()
        self.get_csrf_token()
        for cookie in self.driver.get_cookies():
            if cookie['name'] == 'cisession':
                self.cookie = {
                    'cisession': cookie['value']
                }
        channel_mode = channel_mode == 'True'
        keyword_mode = keyword_mode == 'True'
        self.logger.info(f'Channel Crawling Mode: {channel_mode}')
        self.logger.info(f'Keyword Crawling Mode: {keyword_mode}')
        self.channel_ids = {}
        if channel_mode:
            self.logger.info(f'Get Channel list ids')
            self.check_artist_channel()
        self.keyword_ids = {}
        if keyword_mode:
            self.logger.info(f'Get Keyword list ids')
            self.check_keyword()
            
        if (from_date == '') ^ (to_date == ''):
            print('Error, from_date and to_date must insert together')
            sys.exit(1)
        elif from_date != '':
            self.from_date = datetime.strptime(from_date, '%Y%m%d')
            self.to_date = datetime.strptime(to_date, '%Y%m%d')
        else:
            self.from_date = datetime.now()
            self.to_date = datetime.now()
    
    def crowdtangle_login(self):
        self.driver.get('https://apps.crowdtangle.com')
        main_window_handle = self.driver.current_window_handle
        self.driver.find_element_by_css_selector('button').click()
        sign_window_handle = None
        while not sign_window_handle:
            for handle in self.driver.window_handles:
                if handle != main_window_handle:
                    sign_window_handle = handle
        self.driver.switch_to.window(sign_window_handle)
        email_input = self.driver.find_element_by_css_selector('#email.inputtext')
        email_input.send_keys(CROWDTANGLE_EMAIL)
        pass_input = self.driver.find_element_by_css_selector('#pass.inputtext')
        pass_input.send_keys(CROWDTANGLE_PASSWORD)
        self.driver.find_element(By.XPATH, '//*[@id="loginbutton"]').click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[1]/h1'))
        )

    def get_csrf_token(self):
        self.driver.get(CROWDTANGLE_FB_LINK)
        script_text = self.driver.page_source
        raw_token = re.search('csrf_token: \'.*\'', script_text)[0]
        self.csrf_token = raw_token[raw_token.find('\'')+1:raw_token.rfind('\'')]
    
    def check_artist_channel(self):
        self.driver.get(CROWDTANGLE_FB_LINK)
        while True:
            self.driver.implicitly_wait(1)
            soup = bs(self.driver.page_source, 'html.parser')
            builded_channel = [x.text for x in soup.select('.rc-collapse-content-active .list-item-group a')]
            if len(builded_channel) > 0:
                break
        for artist in self.channels:
            if artist not in builded_channel:
                while True:
                    now_url = self.driver.current_url
                    create_list_btn = self.driver.find_element(By.CSS_SELECTOR, 'div.create-list')
                    create_list_btn.click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR,
                            'img[alt="FB pages icon"]'
                        ))
                    )
                    self.driver.find_element_by_css_selector('img[alt="FB pages icon"]').click()
                    try:
                        WebDriverWait(self.driver, 10).until(EC.url_changes(now_url))
                        break
                    except:
                        self.driver.get(CROWDTANGLE_FB_LINK)
                channel_name = self.driver.find_element_by_css_selector('div.dashboard-name-container input')
                channel_name.send_keys(artist)
                submit_btn = self.driver.find_element_by_css_selector('div.dashboard-name-container button')
                submit_btn.click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        'span.edit-report-title-icon > i'
                    ))
                )
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        '.ui-searchbar-main input'
                    ))
                )
                channel_link = self.driver.find_element_by_css_selector('.ui-searchbar-main input')
                channel_link.send_keys(self.channels[artist])
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'div.add-producer-result'
                    ))
                )
                for tag in self.driver.find_elements_by_css_selector('.add-producer-result'):
                    action = ActionChains(self.driver)
                    action.move_to_element(tag).perform()
                    try:
                        tooltip_text = tag.find_element_by_css_selector('.ct-tooltip').get_attribute("innerHTML").strip()
                    except:
                        tooltip_text = tag.find_element_by_css_selector('a').text.strip()
                    if tooltip_text == self.channels[artist]:
                        tag.find_element_by_css_selector('button').click()
                        break
        soup = bs(self.driver.page_source, 'html.parser')
        for tag in soup.select('.list-item-group a'):
            if tag.text in self.channels:
                self.channel_ids[tag.text] = tag['href'][tag['href'].rfind('/') + 1:]
        
    def check_keyword(self):
        self.driver.get(CROWDTANGLE_FB_LINK+'/search/new')
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                '//*[@id="body-container-inner"]/div[2]/div[5]/div[2]/div[2]/div[1]/div/div[1]'
            ))
        )
        soup = bs(self.driver.page_source, 'html.parser')
        builded_keyword = [x.text for x in soup.select('.rc-collapse-content-active .list-item-group a')]
        for keyword in self.keywords:
            if keyword not in builded_keyword:
                keyword_input = self.driver.find_element_by_css_selector('input.advanced-search-input')
                keyword_input.send_keys(keyword)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 
                        '.react-save-search-button'
                    ))
                )
                submit_btn = self.driver.find_element_by_css_selector('button.react-save-search-button')
                submit_btn.click()
                self.driver.get(CROWDTANGLE_FB_LINK+'/search/new')
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH, 
                        '//*[@id="body-container-inner"]/div[2]/div[5]/div[2]/div[2]/div[1]/div/div[1]'
                    ))
                )
        soup = bs(self.driver.page_source, 'html.parser')
        for tag in soup.select('.rc-collapse-content-active .list-item-group a'):
            if tag.text in self.keywords:
                self.keyword_ids[tag.text] = tag['href'][tag['href'].rfind('/') + 1:]
    
    def start_requests(self):
        pivot = self.from_date
        while pivot <= self.to_date:
            form_data={
                'csrf_token': self.csrf_token,
                'start_date': pivot.strftime('%Y-%m-%d 00:00:00'),
                'end_date': pivot.strftime('%Y-%m-%d 23:59:59')
            }
            for keyword in self.keyword_ids:
                yield scrapy.FormRequest(
                    f'{CROWDTANGLE_FB_LINK}/{self.keyword_ids[keyword]}/stream/popular/0/1/0/0/0/0/custom/raw/0/2,3',
                    self.parse_post,
                    method='POST',
                    meta={
                        'by': 'keyword', 'keyword': keyword, 
                        'id': self.keyword_ids[keyword], 
                        'crawled_item_cnt': 0
                    },
                    cookies=self.cookie,
                    formdata=form_data
                )
            for channel in self.channel_ids:
                yield scrapy.FormRequest(
                    f'{CROWDTANGLE_FB_LINK}/{self.channel_ids[channel]}/stream/popular/0/1/0/0/0/0/custom/raw/0/2,3',
                    self.parse_post,
                    method='POST',
                    meta={
                        'by': 'channel', 'channel': f'{channel}', 
                        'id': self.channel_ids[channel], 
                        'crawled_item_cnt': 0
                    },
                    cookies=self.cookie,
                    formdata=form_data
                )
            pivot += timedelta(days=1)

    def parse_post(self, response):
        soup = bs(response.body, 'html.parser')
        crawled_item_cnt = response.meta['crawled_item_cnt']
        limit = min(self.post_per_day- crawled_item_cnt, len(soup.select('.feed_item')))
        post_list = data_producer = response.xpath("/html/body/div[@class='stream_container']/ul/li[@data-producer-name]")
        for data in post_list.getall():
            post = bs(data, 'html.parser').find('li')
            # for post in list(soup.select('.feed_item'))[:limit]:
            channel_name = post['data-producer-name'].strip()
            page_id = post['data-external-id']
            page_id, post_id = page_id.split('_')
            post_url = f'https://www.facebook.com/{page_id}/posts/{post_id}'
            post_body = post.select_one('.message').text.strip()
            
            post_stat = {}
            for stat_item in post.select('.stat_bar_item'):
                if len(stat_item.select('img')) == 0:
                    continue
                elif len(stat_item.select('img')) > 1:
                    reaction_soup = bs(stat_item['data-reactions'], 'html.parser')
                    reaction_cnt = re.split('<[^>]*>', stat_item['data-reactions'])[1:]
                    # post_stat['total'] = reaction_cnt
                    for idx, reaction in enumerate(reaction_soup.select('img')):
                        stat_name = reaction['src']
                        stat_name = re.search('new-.+-icon', stat_name)[0][4:-5]
                        stat_val = int(reaction_cnt[idx].replace(',', ''))
                        post_stat[stat_name] = stat_val
                else:
                    stat_name = stat_item.select_one('img')['src']
                    stat_name = re.search('new-.+-icon', stat_name)[0][4:-5]
                    stat_val = int(stat_item.text.strip().replace(',', ''))
                    post_stat[stat_name] = stat_val
            
            post_date = post.select_one('.timestamp-tooltip')['title'][:-4]
            if re.match('\d\d\/\d\d\/\d\d\d\d', post_date):
                post_date = datetime.strptime(post_date, '%m/%d/%Y %H:%M%p')
            else:
                post_date = datetime.strptime(post_date, '%H:%M%p')
                post_date = post_date.replace(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day,
                )
            yield FBItem(
                data_id=page_id+'_'+post_id,
                channel=channel_name,
                post_url=post_url,
                body=post_body,
                create_dt=post_date,
                stat=post_stat,
                by=response.meta['by']+':'+response.meta[response.meta['by']]
            )
        crawled_item_cnt += limit
        response.meta['crawled_item_cnt'] = crawled_item_cnt
        if crawled_item_cnt < self.post_per_day and limit == 12:
            yield scrapy.Request(
                f'{CROWDTANGLE_FB_LINK}/{response.meta["id"]}/stream/popular/0/1/{response.meta["crawled_item_cnt"]}/0/0/0/1day/raw/0/2,3',
                self.parse_post,
                meta=response.meta,
                cookies=self.cookie
            )