from django.db import models
from Guest.models import tbl_user
# Create your models here.

class tbl_chatold(models.Model):
    message = models.TextField()
    reciver = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='received_messages')
    sender = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='sent_messages')
    datetime = models.DateTimeField(auto_now_add=True)
    file_data = models.BinaryField(null=True, blank=True)  # Store file data
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # Store file size in bytes