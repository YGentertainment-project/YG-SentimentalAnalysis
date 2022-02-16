from ast import excepthandler
import os
from django.shortcuts import render
from clipping.serializers import GroupSerializer
from utils.api import APIView, validate_serializer
from .models import Keyword, KeywordGroup, Group, GroupKeyword, GroupSchedule, GroupUser
from rest_framework.parsers import JSONParser

def base(request):
    '''
    general page
    '''
    # db연결 필요
    groups = Group.objects.filter()
    keywords = Keyword.objects.all()
    print(groups)
    print(keywords)
    values = {
        'groups': ['그룹1', '그룹2'],
        'keywords': ['키워드1', '키워드2', '키워드3', '키워드4', '키워드5', '키워드6', '키워드7', '키워드8', '키워드9', '키워드10'
        , '키워드11', '키워드12', '키워드13', '키워드14', '키워드15', '키워드16', '키워드17', '키워드18'
        , '키워드19', '키워드20', '키워드21', '키워드22', '키워드23', '키워드24', '키워드25', '키워드26'],
    }
    return render(request, 'clipping/clipping.html', values)

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
        Clipping Group Create API
        '''
        data = request.data
        print(data)
        try:
            # Create Clipping Group
            group_data = []
            group_data.append(data["name"])
            group_data.append(data["collect_date"])
            group = Group.objects.create(**group_data)
        except:
            return self.error("cannot create Clipping Group")
        else:
            try:
                # Create Clipping Group Users
                for user in data["users"]:
                    group_user_data = [ group ]
                    group_user_data.append(user["name"])
                    group_user_data.append(user["email"])
                    GroupUser.objects.create(**group_user_data)
            except:
                return self.error("cannot create Clipping Group users")
            
            try:
                # Create Clipping Group Keyword
                for keyword in data["keywords"]:
                    group_keyword_data = [ group ]
                    group_keyword_data.append(keyword)
                    GroupKeyword.objects.create(**group_keyword_data)
            except:
                return self.error("cannot create Clipping Group keywords")

            try:
                # Create Clipping Group Schedule
                for schedule in data["schedules"]:
                    group_schedule_data = [ group ]
                    group_schedule_data.append(schedule)
                    GroupSchedule.objects.create(**group_schedule_data)
            except:
                return self.error("cannot create Clipping Group schedules")
        
        return self.success(GroupSerializer(group).data)
    
    def put(self, request):
        '''
        Clipping Group Update API
        '''
        data = request.data
        try:
            # Create Clipping Group
            group_data = []
            group_data.append(data["name"])
            group_data.append(data["collect_date"])
            group = Group.objects.update(**group_data)
        except:
            return self.error("cannot create Clipping Group")
        else:
            try:
                # Create Clipping Group Users
                for user in data["users"]:
                    group_user_data = [ group ]
                    group_user_data.append(user["name"])
                    group_user_data.append(user["email"])
                    GroupUser.objects.update(**group_user_data)
            except:
                return self.error("cannot create Clipping Group users")
            
            try:
                # Create Clipping Group Keyword
                for keyword in data["keywords"]:
                    group_keyword_data = [ group ]
                    group_keyword_data.append(keyword)
                    GroupKeyword.objects.update(**group_keyword_data)
            except:
                return self.error("cannot create Clipping Group keywords")

            try:
                # Create Clipping Group Schedule
                for schedule in data["schedules"]:
                    group_schedule_data = [ group ]
                    group_schedule_data.append(schedule)
                    GroupSchedule.objects.update(**group_schedule_data)
            except:
                return self.error("cannot create Clipping Group schedules")
        
        return self.success(GroupSerializer(group).data)
