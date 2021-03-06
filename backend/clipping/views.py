from distutils.command import check
import os
import json
import datetime
import traceback 
import openpyxl
from pymongo import MongoClient
from openpyxl import load_workbook
from openpyxl.writer.excel import save_virtual_workbook
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from clipping.NLPDB.NLPData import NLPData, NLPCloud
from clipping.serializers import GroupKeywordSerializer, GroupScheduleSerializer, GroupSerializer, GroupUserSerializer
from utils.api import APIView, validate_serializer
from .models import Keyword, KeywordGroup, Group, GroupKeyword, GroupSchedule, GroupUser
from crawler.scrapy_app.apikey import *

def base(request):
    '''
    general page
    '''
    if request.method == 'GET':
        '''
        general page
        '''
        groups = Group.objects.all().values()
        keywords = KeywordGroup.objects.all().values()

        #========================================================#
        # Search ALL Keyword Groups for display                  #
        #========================================================#
        keyword_list = []
        for keyword in keywords:
            keyword_list.append(keyword["groupname"])

        values = {
            'groups': groups,
            'keywords': keyword_list,
            'first_depth' : 'NEWS 클리핑',
            'second_depth': 'NEWS 클리핑',
        }

        return render(request, 'clipping/clipping.html', values)
    else:
        type = request.POST['type']
        if type == 'receiver_download':
            '''
            export to excel (mail receiver download)
            '''
            group_id = request.POST.get('group_id', None) #그룹 id
            try:
                group = Group.objects.filter(id=group_id).first()
            except:
                return JsonResponse(data={"success":False, "data": "Clipping Group does not exist"})
            group_name = getattr(group, "name")

            wb = openpyxl.Workbook()
            sheet = wb.active

            #========================================================#
            # Search Group User list of this group                   #
            #========================================================#
            users = GroupUser.objects.filter(group_id=group_id).values()
            user_list = []
            email_list = []

            for user in users:
                user_list.append(user["name"])
                email_list.append(user["email"])

            #========================================================#
            # Make User list Excel sheet                             #
            #========================================================#
            i=1
            for ii, name in enumerate(user_list):
                sheet["A"+str(i)] = name
                sheet["B"+str(i)] = email_list[ii]
                i+=1

            filename = "%s USER LIST.xlsx" % (group_name)
            response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename='+filename
            return response
        elif type == 'keyword_download':
            '''
            export to excel (keyword download)
            '''
            try:
                keyword_groups = KeywordGroup.objects.all()
                keywords = Keyword.objects.all()
                if keyword_groups.exists():
                    keyword_table = {}
                    for keyword_group in keyword_groups:
                        keyword_table[keyword_group.groupname] = []
                    for keyword in keywords:
                        keyword_table[keyword.keywordgroup.groupname].append(keyword.keyword)
                    max_column = max([len(keywords) for _, keywords in keyword_table.items()])
                    new_wb = openpyxl.Workbook()
                    new_ws = new_wb.active
                    new_ws.cell(1, 1, '키워드')
                    for col in range(2, max_column + 1):
                        new_ws.cell(1, col, f'동의어{col - 1}')
                    new_ws.cell(1, max_column + 1, '종류')
                    for idx1, keyword_group in enumerate(keyword_groups):
                        groupname = keyword_group.groupname
                        new_ws.cell(idx1 + 2, 1, groupname)
                        for idx2, synonym in enumerate(keyword_table[groupname][1:]):
                            new_ws.cell(idx1 + 2, idx2 + 2, synonym)
                        new_ws.cell(idx1 + 2, max_column + 1, keyword_group.type)
                    filename = 'Keyword.xlsx'
                    file_response = HttpResponse(
                        save_virtual_workbook(new_wb),
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    file_response['Content-Disposition'] = f'attachment;filename*=UTF-8\'\'{filename}'
                    return file_response
                else:
                    return request.success()
            except Exception as e:
                return request.error("Keyword Group does not exist")


def preview(request):
    '''
    preview page
    '''
    try:
        group_id = request.GET['group_id']
        group = Group.objects.filter(id=group_id).first()
        if group is None:
            return JsonResponse(data={"fail":False, "data": "Clipping Group does not exist"})
        # 클리핑 그룹의 키워드 목록 수집
        keywords = GroupKeyword.objects.filter(group=group).values()
        keyword_list = [keyword["keyword"] for keyword in keywords]
        
        # 클리핑 그룹 기간 설정
        today = datetime.datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        # 전일
        if group.collect_date == 0:
            from_date = today - datetime.timedelta(days=1)
            to_date = today - datetime.timedelta(microseconds=1)
        # 당일
        elif group.collect_date == 1:
            from_date = today
            to_date = datetime.datetime.now()
        # 1주
        elif group.collect_date == 2:
            from_date = today - datetime.timedelta(days=7)
            to_date = today - datetime.timedelta(microseconds=1)
        # 1달
        elif group.collect_date == 3:
            from_date = today - datetime.timedelta(days=30)
            to_date = today - datetime.timedelta(microseconds=1)
        # MongoDB 기간 쿼리
        date_query = {'create_dt': {'$gte': from_date, '$lt': to_date}}
        
        # MongoDB 연결
        conn = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
        news_collection = conn[MONGO_DB]['News']
        
        # 뉴스 반응 한국어 변환 테이블
        reaction_ko = {
            'cheer': '응원해요',
            'congrats': '축하해요',
            'expect': '기대해요',
            'like': '좋아요',
            'sad': '슬퍼요',
            'surprise': '놀랐어요'
        }
        # Aspect 한국어 변환 테이블
        asp_ko = {
            'SAB': '가창력',
            'ETC': '기타',
            'FIG': '몸매',
            'REA': '반응',
            'VIB': '분위기',
            'PIC': '사진',
            'SOC': '사회성',
            'CHR': '안무',
            'ALB': '앨범',
            'FAC': '얼굴',
            'ACT': '연기력',
            'MSC': '음악',
            'EVT': '이벤트',
            'ART': '작품성',
            'TMW': '팀워크',
            'FSH': '패션', 
            'PER': '퍼포먼스',
            'POS': '포즈',
            'EXP': '표정',
            'BTY': '뷰티'
        }
        
        # 클리핑 기간에 해당하는 NLP 데이터 수집
        nlp_dataset = NLPData(from_date, to_date, keyword_list)
        # 워드 클라우드 제작용 Frequency 계산
        wordcloud_generator = NLPCloud(nlp_dataset)
        
        data_by_keyword = {keyword:{'keyword_wo_space': keyword.replace(' ','-')} for keyword in keyword_list}
        for keyword in keyword_list:
            # 뉴스 목록 검색
            cursor = news_collection.find(
                {'$and':[date_query, {'keyword':{'$eq': keyword}}]}, 
                allow_disk_use=True).sort('reaction_sum', -1).limit(10)
            data_by_keyword[keyword]['news_list'] = list(cursor)
            for news_item in data_by_keyword[keyword]['news_list']:
                news_item['reaction_ko'] = {
                    reaction_ko[reaction_type]:reaction_value 
                    for reaction_type, reaction_value in news_item['reaction'].items()
                }
            # 빈도수 데이터
            data_by_keyword[keyword]['freq_data'] = wordcloud_generator.single_keyword_cloud(keyword)
            # 감성 분석 데이터
            data_by_keyword[keyword]['absa'] = {}
            # NLP 데이터에서 문서 순회
            for nlp_data in nlp_dataset.data[keyword]:
                # 문서내 문장 순회
                for tag_list in nlp_data['ABSA']:
                    # 문장별 ABSA 태그 순회
                    # asp_tag_type: ASP-OPN 쌍에서 ASP 태그의 종류
                    # asp_tag_text: ASP-OPN 쌍에서 ASP에 해당하는 텍스트
                    # opn_text: ASP-OPN 쌍에서 OPN에 해당하는 텍스트
                    for asp_tag_type, asp_tag_text, opn_text in tag_list:
                        # ASP-ETC 형식에서 ETC만 추출하여 한국어 변환
                        asp_tag_type = asp_ko[asp_tag_type[4:7]]
                        # data_by_keyword[keyword]['absa']는 ASP 태그를 Key로 하는 Dict
                        # Value는 Tuple(int, Dict[str:int]) 전체 등장 횟수, 각 OPN 별 등장 횟수
                        if asp_tag_type not in data_by_keyword[keyword]['absa']:
                            data_by_keyword[keyword]['absa'][asp_tag_type] = [0, {}]
                        data_by_keyword[keyword]['absa'][asp_tag_type][0] += 1
                        if opn_text not in data_by_keyword[keyword]['absa'][asp_tag_type][1]:
                            data_by_keyword[keyword]['absa'][asp_tag_type][1][opn_text] = 0
                        data_by_keyword[keyword]['absa'][asp_tag_type][1][opn_text] += 1
            # 각 Aspect Type 내부에서 Opinion의 등장횟수로 내림차순 정렬
            for aspect_type in data_by_keyword[keyword]['absa']:
                data_by_keyword[keyword]['absa'][aspect_type][1] = \
                    sorted(data_by_keyword[keyword]['absa'][aspect_type][1].items(), key=lambda x: x[1], reverse=True)
            # Aspect Type 등장 횟수에 따라 내림차순 정렬
            data_by_keyword[keyword]['absa'] = \
                sorted(data_by_keyword[keyword]['absa'].items(), key=lambda x: x[1][0], reverse=True)
        values = {
            'today': today,
            'from_date': from_date,
            'to_date': to_date,
            'data_by_keyword': data_by_keyword,
            'first_depth' : 'NEWS 클리핑',
            'second_depth': '미리보기',
        }
        return render(request, 'clipping/preview.html', values)
    except:
        traceback.print_exc()
        return JsonResponse(data={"success":False, "data": "Internal Server Error"})

# KeywordAPI
# Keyword Groups Excel Handling
# | get: Download Keyword Excel
# | post: Create/Update Keyword Excel
# Author: 곽재원, tsfo1489@gmail.com
class KeywordAPI(APIView):
    def get(self, request):
        '''
        Download Keyword Group Excel
        REQUEST FORMAT: None
        RESPONSE FORMAT: Excel 
        '''
        try:
            # 키워드 그룹 및 키워드 종합
            keyword_groups = KeywordGroup.objects.all()
            keywords = Keyword.objects.all()
            if keyword_groups.exists():
                # { 키워드그룹:List[키워드] }
                keyword_table = {}
                for keyword_group in keyword_groups:
                    keyword_table[keyword_group.groupname] = []
                for keyword in keywords:
                    keyword_table[keyword.keywordgroup.groupname].append(keyword.keyword)
                # 최대 동의어 개수 카운트
                max_column = max([len(keywords) for _, keywords in keyword_table.items()])
                new_wb = openpyxl.Workbook()
                new_ws = new_wb.active
                # 최상단 컬럼명 작성 (키워드, 동의어1, 동의어2, ..., 종류)
                new_ws.cell(1, 1, '키워드')
                for col in range(2, max_column + 1):
                    new_ws.cell(1, col, f'동의어{col - 1}')
                new_ws.cell(1, max_column + 1, '종류')
                # 키워드 그룹 및 동의어 작성
                for idx1, keyword_group in enumerate(keyword_groups):
                    groupname = keyword_group.groupname
                    new_ws.cell(idx1 + 2, 1, groupname)
                    for idx2, synonym in enumerate(keyword_table[groupname][1:]):
                        new_ws.cell(idx1 + 2, idx2 + 2, synonym)
                    new_ws.cell(idx1 + 2, max_column + 1, keyword_group.type)
                # Excel 파일 Response 생성
                filename = 'Keyword.xlsx'
                file_response = HttpResponse(
                    save_virtual_workbook(new_wb),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                file_response['Content-Disposition'] = f'attachment;filename*=UTF-8\'\'{filename}'
                return file_response
            else:
                return self.success()
        except Exception as e:
            return self.error("Keyword Group does not exist")

    def post(self, request):
        '''
        Keyword list Excel Import
        '''
        keywordfile = request.FILES['KeywordFile']
        keywordfile = openpyxl.load_workbook(keywordfile)
        worksheet = keywordfile[keywordfile.sheetnames[0]]
        column_max = 1
        while True:
            x = worksheet.cell(row=1, column=column_max).value
            column_max += 1
            if x is None:
                break
        row = 2
        keyword_table = {}
        while True:
            keyword_groupname = worksheet.cell(row=row, column=1).value
            if keyword_groupname is None:
                break
            keyword_table[keyword_groupname] = [keyword_groupname]
            for col in range(2, column_max):
                keyword = worksheet.cell(row=row, column=col).value
                if keyword is not None:
                    keyword_table[keyword_groupname].append(keyword)
            row += 1
        Keyword.objects.all().delete()
        KeywordGroup.objects.all().delete()
        for keyword_group in keyword_table:
            group_item = KeywordGroup.objects.create(
                groupname = keyword_group,
                type = keyword_table[keyword_group][-1],
                news_platform = True,
                sns_platform = True
            )
            for keyword in keyword_table[keyword_group][:-1]:
                Keyword.objects.create(
                    keywordgroup = group_item,
                    keyword = keyword
                )
        return self.success(keyword_table)


# CLippingGroupAPI
# CRUD NEWS Clipping Groups by using 
# | get: Read Clipping Groups
# | post: Create/Update Clipping Groups
# | delete: Delete Clipping Groups
# Author: 최영우, cyw7515@naver.com
class ClippingGroupAPI(APIView):
    def get(self, request):
        '''
        Read Clipping Group API
        REQUEST FORMAT:
        {
            "group_id": group_id (num)
        }
        RESPONSE FORMAT:
        {
            "name": group_name(str),
            "collect_date": 수집기간(T:당일, F:어제) (boolean),
            "checked_keywords": 선택한 키워드 목록 (str list),
            "schedules": 수집시기 (datetime list),
        }
        '''
        group_id = request.GET.get("group_id")
        if not group_id:
            return self.error()
        
        try:
            group = Group.objects.filter(id=group_id).first()
        except:
            return self.error("Clipping Group does not exist")
        
        #========================================================#
        # Search Group Keyword List for this group               #
        #========================================================#
        check_list = []
        checked_keywords = GroupKeyword.objects.filter(group_id=group_id).values()
        for key in checked_keywords:
            check_list.append(key["keyword"])

        #========================================================#
        # Search Group schedule List for this group               #
        #========================================================#
        schedule_list = []
        schedules = GroupSchedule.objects.filter(group_id = group_id).values()
        for key in schedules:
            schedule_list.append(key["time"])

        #========================================================#
        # Make Response data                                     #
        #========================================================#
        if group:
            res_data = {}
            res_data["name"] = getattr(group, "name")
            res_data["collect_date"] = getattr(group, "collect_date")
            # data["total_keywords"] = total_keywords
            res_data["checked_keywords"] = check_list
            res_data["schedule"] = schedule_list
            return JsonResponse(data={"success":True, "data": res_data})
        else:
            return self.error("Request does not have any group name")
        
    
    def post(self, request):
        '''
        Create/Update Clipping Group API
        REQUEST FORMAT:
        {
            "user": group에 포함된 user list excel 파일 (file),
            "body":{
                "name": group name (str),
                "collect_data": 그룹 수집 기간(0: 어제, 1: 당일 2: 1주 3: 1달) (int),
                "keywords":선택한 키워드 목록 (str list),
                "schedules": 수집 시기 (datetime list)
            } ==> string으로 전달됨, json.loads(data["body"]) 필수
        }
        RESPONSE FORMAT:
        {
            "success": True/False (boolean),
            "group": 생성된 그룹의 group_id (int)
        }
        '''
        data = request.POST
        create_user_flag = False

        # 'not in data' means 'in FILES', so there is an attached file
        if 'users' not in data:
            file = request.FILES['users']
            create_user_flag = True
        
        data = json.loads(data['body'])
        # data = JSONParser(data)
        
        try:
            # Create Clipping Group
            group_data = {
                "name": data["name"],
                "collect_date": data["collect_date"]
            }
            exist_data = Group.objects.filter(name=data["name"]).first()
            #========================================================#
            # Create new Group if there are not same name group      #
            #========================================================#
            if exist_data is None:
                group = GroupSerializer(data=group_data)
                if group.is_valid():
                    group.save()
                else:
                    return self.error("Create clipping group data is not valid")
            #========================================================#
            # Update Group data if there is a same name group        #
            #========================================================#
            else:
                # new_data = GroupSerializer(exist_data).data
                group = GroupSerializer(exist_data, data=group_data)
                if group.is_valid():
                    group.save()
                else:
                    return self.error("Update clipping group data is not valid")
        except:
            return self.error("cannot create Clipping Group")
        
        group_id = group.data["id"]
        
        # Create Clipping Group Users
        if create_user_flag:
            try:
                #========================================================#
                # Load Excel for external User List...                   #
                #========================================================#
                
                load_wb = load_workbook(file, data_only=True)
                load_ws = load_wb['Sheet1']
                
                user_list = []

                for row in load_ws.rows:
                    # Excel Format should be name, email, name, email...
                    user_tuple = []
                    for cell in row:
                        # [[name, email], [name, email], ...]
                        user_tuple.append(cell.value)
                    user_list.append(user_tuple)
                #========================================================#

                # To reflect add, update, remove user... delete all in this group
                GroupUser.objects.filter(group_id=group_id).delete()
                
                #========================================================#
                # Create Group Users in this Group                       #
                #========================================================#
                for user in user_list:
                    group_user_data = {
                        "group": group_id,
                        "name": user[0],
                        "email": user[1]
                    }
                    group_user = GroupUserSerializer(data=group_user_data)
                    if group_user.is_valid():
                        group_user.save()
                    else:
                        return self.error("Create group user data is not valid")
                #========================================================#
            except:
                return self.error("cannot create Clipping Group users")
        
        # Create Clipping Group Keyword
        try:
            # To reflect add, update, remove keyword... delete all in this group
            GroupKeyword.objects.filter(group_id=group_id).delete()

            #========================================================#
            # Create Group Keywords in this Group                    #
            #========================================================#
            for keyword in data["keywords"]:
                # print("pass key: " + keyword)
                group_keyword_data = {
                    "group": group_id,
                    "keyword": keyword
                }
                group_keyword = GroupKeywordSerializer(data=group_keyword_data)
                if group_keyword.is_valid():
                    group_keyword.save()
                else:
                    return self.error("Create group keyword data is not valid")
            #========================================================#
        except:
            return self.error("cannot create Clipping Group keywords")
        
        # Create Clipping Group Schedule
        try:
            # To reflect add, update, remove schedule... delete all in this group
            GroupSchedule.objects.filter(group_id=group_id).delete()

            #========================================================#
            # Create Group Schedules in this Group                   #
            #========================================================#
            for schedule in data["schedules"]:
                # print("pass sch: " + schedule)
                hour = int(schedule[0:2])
                min = int(schedule[3:5])
                group_schedule_data = {
                    "group": group_id,
                    "time": datetime.time(hour, min, 0)
                }
                group_schedule = GroupScheduleSerializer(data=group_schedule_data)
                if group_schedule.is_valid():
                    group_schedule.save()
                else:
                    return self.error("Create group schedule data is not valid")
            #========================================================#
        except:
            return self.error("cannot create Clipping Group schedules")

        return JsonResponse(data={"success":True, "group": group_id})

    def delete(self, request):
        """
        Delete Clipping Group API
        REQUEST FORMAT:
        {
            "group_id": 그룹 아이디 (num)
        }
        RESPONSE FORMAT:
        {
            "success": True/False (boolean)
        }
        """
        group_id = request.GET.get("group_id")
        
        if group_id is None:
            return self.error("Group id does not exist")
        
        Group.objects.filter(id=group_id).delete()
        #Group keyword, user, schedule is deleted automatically by CASCADE

        return JsonResponse(data={"success":True})
