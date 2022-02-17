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
    keyword_list = [key.groupname for key in KeywordGroup.objects.all()]
    return render(request, 'report/report.html', {'keyword_list': keyword_list})


def preview(request):
    '''
    preview page
    '''
    return render(request, 'report/preview.html')
    

def load_data(request):
    conn = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
    db = conn.crawling_tuto
    col = db.News

    start = int(request.GET['start'])
    length = int(request.GET['length'])

    sort_table = {
        "0": "title",
        "1": "keyword",
        "2": "create_dt",
        "3": "press",
    }

    searchTitle = request.GET['columns[0][search][value]']
    searchPress = request.GET['columns[3][search][value]']
    searchDate = request.GET['columns[2][search][value]']
    searchKeyword = request.GET['columns[1][search][value]']
    total_length = col.count_documents({})
    filtered_length = total_length
    
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
    print(search_query)
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
    for idx in range(len(news_list)):
        del news_list[idx]['_id']
    print(news_list[:5])
    print(total_length)
    print(filtered_length)
    return JsonResponse({
        'draw': request.GET['draw'],
        'recordsTotal': total_length,
        'recordsFiltered': filtered_length,
        'data': news_list,
    })    



