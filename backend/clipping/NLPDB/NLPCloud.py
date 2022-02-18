from collections import Counter
from typing import Dict
from wordcloud import WordCloud
from clipping.NLPDB.NLPData import NLPData
from crawler.scrapy_app.apikey import *

class NLPCloud:
    def __init__(self, data: NLPData):
        self.data = data.data
    
    def single_keyword_cloud(
                  self,
                  keyword, 
                  length_threshold = 1,
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
                'MIX': '',
                'NER': '',
                'POS': ''
            }
        #POS
        pos_counter = Counter(POS_words) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함
        wc = WordCloud(
                       font_path='./clipping/NLPDB/font/NanumGothic.ttf',
                       background_color='white', 
                       width=1000, 
                       height=1000, 
                       scale=2.0, 
                       max_font_size=200,
                       min_word_length=length_threshold)
        gen = wc.generate_from_frequencies(pos_counter)
        POS_svg = gen.to_svg()

        #NER
        ner_counter = Counter(NER_words)
        gen = wc.generate_from_frequencies(ner_counter)
        NER_svg = gen.to_svg()

        #MIX
        mix_counter = Counter(NER_words)
        gen = wc.generate_from_frequencies(mix_counter)
        MIX_svg = gen.to_svg()

        return {
            'MIX': MIX_svg,
            'NER': NER_svg,
            'POS': POS_svg
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
                'MIX': '',
                'NER': '',
                'POS': ''
            }
        #POS
        pos_counter = Counter(POS_words) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함
        wc = WordCloud(
                       font_path='./clipping/NLPDB/font/NanumGothic.ttf',
                       background_color='white', 
                       width=350, 
                       height=150, 
                       scale=2.0, 
                       max_font_size=200,
                       min_word_length=length_threshold)
        gen = wc.generate_from_frequencies(pos_counter)
        POS_svg = gen.to_svg(embed_font=True, embed_image=True)

        #NER
        ner_counter = Counter(NER_words)
        gen = wc.generate_from_frequencies(ner_counter)
        NER_svg = gen.to_svg(embed_font=True, embed_image=True)

        #MIX
        mix_counter = Counter(NER_words)
        gen = wc.generate_from_frequencies(mix_counter)
        MIX_svg = gen.to_svg(embed_font=True, embed_image=True)

        return {
            'MIX': MIX_svg,
            'NER': NER_svg,
            'POS': POS_svg
        }