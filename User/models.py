from django.db import models
from Guest.models import *
# Create your models here.

class tbl_chat(models.Model):
    sender = models.ForeignKey(tbl_user,related_name='sender', on_delete=models.CASCADE)
    reciver = models.ForeignKey(tbl_user,related_name='reciver', on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True)