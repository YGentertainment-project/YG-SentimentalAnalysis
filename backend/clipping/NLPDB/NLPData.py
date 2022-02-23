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
            conn = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
            self.NLP_collection = conn[MONGO_DB]['NewsNLP']
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
                  length_threshold = 2,
                  pos_tag_filter = ['NNG', 'NNP', 'VV', 'VP'],
                  ner_tag_filter = ['PER', 'AFW']) -> Dict[str, str]:
        #POS
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