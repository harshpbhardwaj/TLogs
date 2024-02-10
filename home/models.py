from django.db import models
from django.conf import settings

# Create your models here.
class Login(models.Model):
    email = models.CharField(max_length=122)
    fname = models.CharField(max_length=12)
    mname = models.CharField(max_length=12)
    lname = models.CharField(max_length=12)
    phone = models.CharField(max_length=12)
    password = models.CharField(max_length=122)
    dp = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    country = models.CharField(max_length=90)
    terms = models.CharField(max_length=5)
    date = models.DateTimeField()
    
class Tlogs(models.Model):
    # email = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    email = models.CharField(max_length=122)
    title = models.CharField(max_length=195)
    publish = models.IntegerField(blank=True, null=True)
    views = models.IntegerField(blank=True, default='0', null=True)
    date = models.DateTimeField()
    # def __str__(self):
    #     return str(self.id) + " - " + str(self.title) + " - " + str(self.date)
    
class Tlog_body(models.Model):
    # tlog_id = models.IntegerField()
    tlog = models.ForeignKey(Tlogs, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=122, blank=True, null=True)
    title = models.CharField(max_length=195, blank=True, null=True)
    date = models.DateField()
        
class Tlog_comment(models.Model):
    tlog = models.ForeignKey(Tlogs, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=122, blank=True, null=True)
    date = models.DateTimeField()