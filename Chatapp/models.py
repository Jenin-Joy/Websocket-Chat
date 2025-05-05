from django.db import models
from Guest.models import tbl_user

# Create your models here.
class tbl_chat(models.Model):
    message = models.CharField(max_length=500)
    reciver = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='reciver')
    sender = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='sender')
    datetime = models.DateTimeField()
    file_data = models.BinaryField(null=True, blank=True)  # Store file data
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # Store file size in bytes
