from django.shortcuts import render
from Guest.models import tbl_user

# Create your views here.

def chat(request, id):
    user = tbl_user.objects.get(id=id)
    return render(request,"Chatapp/Chat.html",{"sender":request.session["uid"],"reciver":id,"user":user})