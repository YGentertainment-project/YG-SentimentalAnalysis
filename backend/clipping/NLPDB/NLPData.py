import json
import traceback
from pymongo import MongoClient
from datetime import datetime
from crawler.scrapy_app.apikey import *
from collections import Counter
from typing import Dict
from wordcloud import WordCloud

class NLPData:
    def __init__(self, from_date: datetime, to_date: datetime, keywords):
        try:
            # NLP 데이터 DB 연결
            conn = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
            self.NLP_collection = conn[MONGO_DB]['NewsNLP']
            # to_date 기간 설정 23:59:59로 변경하여 검색
            to_date = to_date.replace(hour=23, minute=59, second=59)
            cursor = self.NLP_collection.find(
                {
                    '$and': [
                        {'create_dt': {'$gte': from_date, '$lte': to_date}},
                        {'keyword': {'$in': keywords}}
                    ]
                }
            )
            self.data = {keyword:[] for keyword in keywords}
            for item in cursor:
                # JSON String 형태로 저장된 데이터 Dictionary로 변환
                item['NER'] = json.loads(item['NER'])
                item['POS'] = json.loads(item['POS'])
                item['ABSA'] = json.loads(item['ABSA'])
                self.data[item['keyword']].append(item)
        except:
            traceback.print_exc()
            Exception('MongoDB Connection Error')
            

class NLPCloud:
    def __init__(self, data: NLPData):
        self.data = data.data
    
    def single_keyword_cloud(
                  self,
                  keyword, 
                  pos_tag_filter = ['NNG', 'NNP', 'VV', 'VP'],
                  ner_tag_filter = ['PER', 'AFW']) -> Dict[str, Dict[str, int]]:
        '''
        Method: single_keyword_cloud
        단일 키워드에 대한 워드 클라우드용 Frequency 데이터 생성기
        
        Args:
            keyword (str): 클라우드 생성 키워드
            pos_tag_filter (List[str], default=['NNG', 'NNP', 'VV', 'VP']):
                형태소 필터, 이에 해당하는 태그만 Frequency 측정
            ner_tag_filter (List[str], default=['PER', 'AFW']):
                개체명 필터, 이에 해당하는 태그만 Frequency 측정
        
        Returns:
            frequency_data (Dict[str, Dict[str, int]]): 
                MIX: NER + POS를 합친 데이터
                NER: 개체명 데이터
                POS: 형태소 데이터
                Dict[str, int]: 태그별 Frequency
        '''
        # POS
        POS_words = []
        NER_words = []
        for item in self.data[keyword]:
            for pos_tags in item['POS']:
                for pos_text, pos_tag in pos_tags:
                    if pos_tag in pos_tag_filter:
                        POS_words.append(pos_text)
            for ner_tags in item['NER']:
                for ner_text, ner_tag in ner_tags:
                    if ner_tag in ner_tag_filter:
                        NER_words.append(ner_text)     
        
        if len(POS_words) == 0 or len(NER_words) == 0:
            return  {
                'MIX': '{}',
                'NER': '{}',
                'POS': '{}'
            }
        #POS
        pos_counter = sorted(dict(Counter(POS_words)).items(), key=lambda x: x[1], reverse=True)
        
        #NER
        ner_counter = sorted(dict(Counter(NER_words)).items(), key=lambda x: x[1], reverse=True)

        #MIX
        mix_counter = sorted(dict(Counter(POS_words + NER_words)).items(), key=lambda x: x[1], reverse=True)
        return {
            'MIX': mix_counter,
            'NER': ner_counter,
            'POS': pos_counter
        }
        
    def multi_keyword_cloud(
                  self,
                  keywords, 
                  length_threshold = 1,
                  pos_tag_filter = ['NNG', 'NNP', 'VV', 'VP'],
                  ner_tag_filter = ['PER', 'AFW']) -> Dict[str, str]:
        #POS
        POS_words = []
        NER_words = []
        for keyword in keywords:
            for item in self.data[keyword]:
                for pos_tags in item['POS']:
                    for pos_text, pos_tag in pos_tags:
                        if pos_tag in pos_tag_filter:
                            POS_words.append(pos_text)
                for ner_tags in item['NER']:
                    for ner_text, ner_tag in ner_tags:
                        if ner_tag in ner_tag_filter:
                            NER_words.append(ner_text)     
        
        if len(POS_words) == 0 or len(NER_words) == 0:
            return  {
                'MIX': '{}',
                'NER': '{}',
                'POS': '{}'
            }
        #POS
        pos_counter = sorted(dict(Counter(POS_words)).items(), key=lambda x: x[1], reverse=True)
        
        #NER
        ner_counter = sorted(dict(Counter(NER_words)).items(), key=lambda x: x[1], reverse=True)

        #MIX
        mix_counter = sorted(dict(Counter(POS_words + NER_words)).items(), key=lambda x: x[1], reverse=True)

        return {
            'MIX': mix_counter,
            'NER': ner_counter,
            'POS': pos_counter
        }