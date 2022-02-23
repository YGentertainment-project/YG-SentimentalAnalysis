from django.db import models
from djongo import models as dmodels


# target은 spider의 이름으로 대체

class Youtube(dmodels.Model):
    data_id = dmodels.TextField(null=False)  # primary
    title = dmodels.CharField(max_length=255, null=True)
    desc = dmodels.TextField(null=True)
    view = dmodels.IntegerField(null=True)
    subs = dmodels.IntegerField(null=True)
    video = dmodels.IntegerField(null=True)
    channelId = dmodels.TextField(null=True)
    create_dt = dmodels.DateTimeField(null=True)
    like = dmodels.IntegerField(null=True)
    videoId = dmodels.TextField(null=True)
    body = dmodels.TextField(null=True)


class News(dmodels.Model):
    _id = dmodels.CharField(max_length=100, null=True)
    data_id = dmodels.IntegerField(null=False)
    press = dmodels.CharField(max_length=100, null=False)
    reporter = dmodels.CharField(max_length=100, null=True)
    title = dmodels.CharField(max_length=255, null=False)
    body = dmodels.TextField(null=False)
    snippet = dmodels.CharField(max_length=100, null=False)
    create_dt = dmodels.DateTimeField(null=False)
    url = dmodels.TextField(null=False)
    keyword = dmodels.CharField(max_length=100, null=False)
    reaction = dmodels.JSONField()
    reaction_sum = dmodels.IntegerField()


class IG(dmodels.Model):
    data_id = dmodels.IntegerField(null=True)
    channel = dmodels.CharField(max_length=255, null=False)
    post_url = dmodels.TextField(null=False)
    post_type = dmodels.CharField(max_length=100, null=False)
    create_dt = dmodels.DateTimeField(null=False)
    body = dmodels.TextField(null=False)
    stat = dmodels.JSONField()
    by = dmodels.CharField(max_length=100, null=False)


class FB(dmodels.Model):
    data_id = dmodels.IntegerField(null=True)
    channel = dmodels.CharField(max_length=255, null=False)
    post_url = dmodels.TextField(null=False)
    create_dt = dmodels.DateTimeField(null=False)
    body = dmodels.TextField(null=False)
    stat = dmodels.JSONField()
    by = dmodels.CharField(max_length=100, null=False)


class Twitter(dmodels.Model):
    data_id = dmodels.IntegerField(null=True)
    create_dt = dmodels.DateTimeField(null=False)
    body = dmodels.TextField(null=False)
    user_id = dmodels.CharField(max_length=100, null=False)
    username = dmodels.CharField(max_length=100, null=False)
    name = dmodels.CharField(max_length=100, null=False)
    lang = dmodels.CharField(max_length=100, null=False)
    keyword = dmodels.CharField(max_length=100, null=False)
    geo = dmodels.CharField(max_length=100, null=False)
    hashtags = dmodels.CharField(max_length=100, null=False)
    object_id = dmodels.CharField(max_length=100, null=False)
    channel = dmodels.CharField(max_length=100, null=False)
