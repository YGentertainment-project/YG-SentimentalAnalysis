from django.db import models
from djongo import models as dmodels

class db_test1(models.Model):
    artist = models.CharField(max_length=100)  # 아티스트 이름
    monthly_listens = models.BigIntegerField(null=True)
    followers = models.BigIntegerField(null=True)
    recorded_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True)
    url1 = models.TextField(null=True)
    url2 = models.TextField(null=True)
    class Meta:
        db_table = "test1"

class db_test2(dmodels.Model):
    first_name = dmodels.CharField(max_length=30)
    last_name = dmodels.CharField(max_length=30)
    class Meta:
        db_table = "test2"