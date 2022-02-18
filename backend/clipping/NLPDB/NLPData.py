import json
import traceback
from pymongo import MongoClient
from datetime import datetime
from crawler.scrapy_app.apikey import *

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
                # item['ABSA'] = json.loads(item['ABSA'])
                self.data[item['keyword']].append(item)
        except:
            traceback.print_exc()
            Exception('MongoDB Connection Error')