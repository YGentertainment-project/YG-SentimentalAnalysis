from ast import excepthandler
import os
import datetime
from re import L
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
    groups = Group.objects.filter()
    keywords = KeywordGroup.objects.all()
    print(groups)
    print(keywords)
    values = {
        'groups': ['그룹1', '그룹2'],
        'keywords': ['키워드1', '키워드2', '키워드3', '키워드4', '키워드5', '키워드6', '키워드7', '키워드8', '키워드9', '키워드10'
        , '키워드11', '키워드12', '키워드13', '키워드14', '키워드15', '키워드16', '키워드17', '키워드18'
        , '키워드19', '키워드20', '키워드21', '키워드22', '키워드23', '키워드24', '키워드25', '키워드26'],
    }
    return render(request, 'clipping/clipping.html', values)

def preview(request):
    '''
    preview page
    '''
    return render(request, 'clipping/preview.html')

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


class ClippingGroupAPI(APIView):
    def get(self, request):
        '''
        Clipping Group Read API
        '''
        group_id = request.GET.get("group_id")
        if not group_id:
            return self.error()
        try:
            group_name = Group.objects.get(id=group_id)["name"]
            total_keywords = list(GroupKeyword.objects.all())
            checked_keywords = list(total_keywords.filter(group_id = group_id).get())
            schedule = list(GroupSchedule.objects.filter(group_id = group_id))
            
            if group_name:
                data = {}
                data["name"] = group_name
                data["total_keywords"] = total_keywords
                data["checked_keywords"] = checked_keywords
                data["schedule"] = schedule
                return self.success(data)
            else:
                return self.error("Request does not have any group name")
        except:
            return self.error("Clipping Group does not exist")
    
    def post(self, request):
        '''
        Clipping Group Create/Update API
        '''
        data = JSONParser().parse(request)
        file = request.FILES['file_excel']

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

        # Create Clipping Group Keyword
        try:
            # To reflect add, update, remove keyword... delete all in this group
            GroupKeyword.objects.filter(group_id=group_id).delete()

            #========================================================#
            # Create Group Keywords in this Group                    #
            #========================================================#
            for keyword in data["keywords"]:
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
        
        return self.success(GroupSerializer(group).data)
