from django.shortcuts import render
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime, timedelta
from crawler.scrapy_app.apikey import *
from clipping.models import KeywordGroup
import traceback

def base(request):
    '''
    general page
    '''
    # 키워드 검색 드롭다운 리스트를 위한 키워드그룹 리스트
    keyword_list = [key.groupname for key in KeywordGroup.objects.all()]
    values = {
            'first_depth' : 'NEWS 데이터',
            'second_depth': 'NEWS 데이터',
            'keyword_list': keyword_list
        }
    return render(request, 'report/report.html', values)


def preview(request):
    '''
    preview page
    '''
    return render(request, 'report/preview.html')
    

def load_data(request):
    # 서버 연결
    conn = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
    db = conn[MONGO_DB]
    col = db.News

    # 전체 데이터 개수
    total_length = col.count_documents({})
    # 검색 시 필터 된 데이터 개수
    filtered_length = total_length
    # 정렬 기능을 위한 sort table 
    sort_table = {
        "0": "title",
        "1": "keyword",
        "2": "create_dt",
        "3": "press",
    }
    # 페이지네이션을 위한 시작점과 데이터 개수
    start = int(request.GET['start'])
    length = int(request.GET['length'])

    # 검색 시 ajax request 파싱(제목, 언론사, 날짜, 키워드)
    searchTitle = request.GET['columns[0][search][value]']
    searchPress = request.GET['columns[3][search][value]']
    searchDate = request.GET['columns[2][search][value]']
    searchKeyword = request.GET['columns[1][search][value]']
    
    # 검색 결과에 따른 MongoDB 검색 쿼리 생성
    search_query = []
    if searchTitle != '':
        search_query.append({'title': {'$regex': searchTitle}})
    if searchPress != '':
        search_query.append({'press': {'$regex': searchPress}})
    if searchKeyword != '':
        search_query.append({'keyword': {'$eq': searchKeyword}})
    if searchDate != '':
        searchDateFrom = datetime.fromisoformat(searchDate.split('~')[0])
        searchDateTo = datetime.fromisoformat(searchDate.split('~')[1]) + timedelta(days=1)
        search_query.append({'create_dt': {'$gte' : searchDateFrom, '$lt' : searchDateTo}})
    
    # 서버에서 데이터 받아오기
    try:
        news_list = list(col
            .find(
                {'$and': search_query} if len(search_query) else {},
                allow_disk_use = True,
            )
            .sort(
                sort_table[request.GET['order[0][column]'][0]],
                1 if request.GET['order[0][dir]'] == 'asc' else -1
            )
            .skip(start)
            .limit(length)
        )
        filtered_length = col.count_documents({'$and': search_query} if len(search_query) else {})
    except:
        traceback.print_exc()

    # 불필요한 MongoDB _id 정보 삭제    
    for idx in range(len(news_list)):
        del news_list[idx]['_id']

    # Datatables에 필요한 데이터 리턴
    return JsonResponse({
        'draw': request.GET['draw'],
        'recordsTotal': total_length,
        'recordsFiltered': filtered_length,
        'data': news_list,
    })