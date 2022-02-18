from enum import unique
from django.db import models

# Create your models here.

class KeywordGroup(models.Model):
    groupname = models.TextField(unique=True)
    type = models.TextField()
    news_platform = models.BooleanField(default=False)
    sns_platform = models.BooleanField(default=False)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "collect_target_keyword_group"


class Keyword(models.Model):
    keywordgroup = models.ForeignKey(KeywordGroup, on_delete=models.CASCADE)
    keyword = models.TextField() # 유의어, 키워드
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "collect_target_keyword"


class Group(models.Model):
    name = models.TextField(unique=True)
    collect_date = models.PositiveSmallIntegerField(default=0)
    # false = yesterday, true = today
    # create_dt = models.DateTimeField(auto_now_add=True)
    # update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clipping_group"


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.TextField(default="")
    email = models.TextField(unique=True)
    # create_dt = models.DateTimeField(auto_now_add=True)
    # update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clipping_group_user"


class GroupSchedule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    time = models.TimeField() # mailing time
    # create_dt = models.DateTimeField(auto_now_add=True)
    # update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clipping_schedule"


class GroupKeyword(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    # keyword = models.ForeignKey(KeywordGroup, on_delete=models.CASCADE)
    keyword = models.TextField()
    # create_dt = models.DateTimeField(auto_now_add=True)
    # update_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clipping_keyword"
