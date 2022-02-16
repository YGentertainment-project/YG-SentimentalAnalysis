from ast import excepthandler
import os
import datetime
from django.shortcuts import render
from clipping.serializers import GroupSerializer, GroupUserSerializer
from utils.api import APIView, validate_serializer
from .models import Keyword, KeywordGroup, Group, GroupKeyword, GroupSchedule, GroupUser
from rest_framework.parsers import JSONParser

def base(request):
    '''
    general page
    '''
    # db연결 필요
    values = {
        'groups': ['그룹1', '그룹2'],
        'keywords': ['키워드1', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2'
        , '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2'
        , '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드2', '키워드냠냠'],
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
        data = next(iter(request.data.dict()))
        print(data.type)
        print(data["keywords"])
        print(data["schedules"])

        # user_list = data["users"]
        # print(user_list)

        try:
            # Create Clipping Group
            group = Group(
                name = data["name"],
                collect_date = data["collect_date"]
            )
            group.save()
        except:
            return self.error("cannot create Clipping Group")

        # try:
        #     # Create Clipping Group Users
        #     for user in user_list:
        #         # group_user_data = [ group.id ]
        #         # group_user_data.append(user["name"])
        #         # group_user_data.append(user["email"])
                
        #         # group_user_data = {
        #         #     "group": group.id,
        #         #     "name": user["name"],
        #         #     "email": user["email"]
        #         # }

        #         group_user = GroupUser(
        #             group_id = group.id,
        #             name = user["name"],
        #             email = user["email"]
        #         )
        #         group_user.save()
        # except:
        #     return self.error("cannot create Clipping Group users")
        
        # try:
        #     # Create Clipping Group Keyword
        #     for keyword in keyword_list:
        #         # group_keyword_data = [ group.id ]
        #         # group_keyword_data.append( keyword )
        #         # GroupKeyword.objects.create(**group_keyword_data)
        #         group_keyword = GroupKeyword(
        #             group_id = group.id,
        #             keyword = keyword
        #         )
        #         group_keyword.save()
        # except:
        #     return self.error("cannot create Clipping Group keywords")

        # try:
        #     # Create Clipping Group Schedule
        #     for schedule in schedule_list:
        #         group_schedule_data = [ group.id ]
        #         group_schedule_data.append( datetime.strptime(schedule, "%H:%M"))
        #         GroupSchedule.objects.create(**group_schedule_data)
        # except:
        #     return self.error("cannot create Clipping Group schedules")
        
        return self.success(GroupSerializer(group).data)
    
    def put(self, request):
        '''
        Clipping Group Update API
        '''
        data = JSONParser().parse(request)
        try:
            # Create Clipping Group
            group_data = []
            group_data.append(data["name"])
            group_data.append(data["collect_date"])
            group = Group.objects.update(**group_data)
        except:
            return self.error("cannot update Clipping Group")
        else:
            try:
                # Check existing user group
                # Create Clipping Group Users
                for user in data["users"]:
                    group_user_data = [ group ]
                    group_user_data.append(user["name"])
                    group_user_data.append(user["email"])
                    GroupUser.objects.update(**group_user_data)
            except:
                return self.error("cannot update Clipping Group users")
            
            try:
                # Create Clipping Group Keyword
                for keyword in data["keywords"]:
                    group_keyword_data = [ group ]
                    group_keyword_data.append(keyword)
                    GroupKeyword.objects.update(**group_keyword_data)
            except:
                return self.error("cannot update Clipping Group keywords")

            try:
                # Create Clipping Group Schedule
                for schedule in data["schedules"]:
                    group_schedule_data = [ group ]
                    group_schedule_data.append(schedule)
                    GroupSchedule.objects.update(**group_schedule_data)
            except:
                return self.error("cannot update Clipping Group schedules")
        
        return self.success(GroupSerializer(group).data)
