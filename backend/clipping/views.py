from distutils.command import check
import os
import datetime 
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from clipping.serializers import GroupKeywordSerializer, GroupScheduleSerializer, GroupSerializer, GroupUserSerializer
from utils.api import APIView, validate_serializer
from .models import Keyword, KeywordGroup, Group, GroupKeyword, GroupSchedule, GroupUser
from rest_framework.parsers import JSONParser
from openpyxl import load_workbook

def base(request):
    '''
    general page
    '''
    # db연결 필요
    groups = Group.objects.all()
    keywords = KeywordGroup.objects.all()
    print(keywords)
    values = {
        'groups': groups,
        'keywords': ['키워드1', '키워드2', '키워드3', '키워드4', '키워드5', '키워드6', '키워드7', '키워드8', '키워드9', '키워드10'
        , '키워드11', '키워드12', '키워드13', '키워드14', '키워드15', '키워드16', '키워드17', '키워드18'
        , '키워드19', '키워드20', '키워드21', '키워드22', '키워드23', '키워드24', '키워드25', '키워드26'],
        'first_depth' : 'NEWS 클리핑',
        'second_depth': 'NEWS 클리핑',
    }
    return render(request, 'clipping/clipping.html', values)

def preview(request):
    '''
    preview page
    '''
    values = {
        'first_depth' : 'NEWS 클리핑',
        'second_depth': '미리보기',
    }
    return render(request, 'clipping/preview.html', values)

class KeywordAPI(APIView):
    def get(self, request):
        '''
        Keyword list read API
        '''
        try:
            keywords = Keyword.objects.all()
            if keywords.exists():
                keyword_list = keywords.values()
                data = []
                for entry in keyword_list:
                    data.append(entry)
                return self.success(data)
            else:
                return self.success()
        except:
            return self.error("Keyword does not exist")

    def post(self, request):
        '''
        Keyword list Excel Import
        '''

class KeywordExcelAPI(APIView):
    def get(self, request):
        '''
        Keyword list read API
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
                max_column = max([len(keywords) for keywords in keyword_table.items()])
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
        print(keyword_table)
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
        return self.success()

class ClippingGroupAPI(APIView):
    def get(self, request):
        '''
        Clipping Group Read API
        '''
        data = request.GET.get("group_id")
        print(data)
        group_id = data
        # print(group_id)
        if not group_id:
            return self.error()
        try:
            group = Group.objects.filter(id=group_id).first()
        except:
            return self.error("Clipping Group does not exist")
        
        # total_keywords = GroupKeyword.objects.all().values()
        # print(total_keywords)
        check_list = []
        checked_keywords = GroupKeyword.objects.filter(group_id=group_id).values()
        for key in checked_keywords:
            check_list.append(key["keyword"])
        print(check_list)

        schedule_list = []
        schedules = GroupSchedule.objects.filter(group_id = group_id).values()
        for key in schedules:
            schedule_list.append(key["time"])
        print(schedule_list)
        
        if group:
            res_data = {}
            res_data["name"] = getattr(group, "name")
            # data["total_keywords"] = total_keywords
            res_data["checked_keywords"] = check_list
            res_data["schedule"] = schedule_list
            return JsonResponse(data={"success":True, "data": res_data})
        else:
            return self.error("Request does not have any group name")
        
    
    def post(self, request):
        '''
        Clipping Group Create/Update API
        '''
        data = JSONParser().parse(request)
        # print(data)
        # if data["users"]:
        #     file = request.FILES['file_excel']

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
            #========================================================#
        except:
            return self.error("cannot create Clipping Group")

        group_id = group.data["id"]

        # Create Clipping Group Users
        # if file:
        #     try:
        #         #========================================================#
        #         # Load Excel for external User List...                   #
        #         #========================================================#
        #         load_wb = load_workbook(file, data_only=True)
        #         load_ws = load_wb['Sheet1']

        #         user_list = []

        #         for row in load_ws.rows:
        #             # Excel Format should be name, email, name, email...
        #             user_tuple = []
        #             for cell in row:
        #                 # [[name, email], [name, email], ...]
        #                 user_tuple.append(cell.value)
        #             user_list.append(user_tuple)
        #         #========================================================#

        #         # To reflect add, update, remove user... delete all in this group
        #         GroupUser.objects.filter(group_id=group_id).delete()
                
        #         #========================================================#
        #         # Create Group Users in this Group                       #
        #         #========================================================#
        #         for user in user_list:
        #             group_user_data = {
        #                 "group": group_id,
        #                 "name": user[0],
        #                 "email": user[1]
        #             }
        #             group_user = GroupUserSerializer(data=group_user_data)
        #             if group_user.is_valid():
        #                 group_user.save()
        #             else:
        #                 return self.error("Create group user data is not valid")
        #         #========================================================#
        #     except:
        #         return self.error("cannot create Clipping Group users")

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

        return JsonResponse(data={"success":True})
        return self.success(GroupSerializer(group).data)

    def delete(self, request):
        group_id = request.Get.get("group_id")