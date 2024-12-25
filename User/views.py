from django.shortcuts import render
from Guest.models import *
from User.models import *
from django.db.models import Q 

# Create your views here.

def homepage(request):
    user = tbl_user.objects.exclude(id=request.session["uid"])
    return render(request,"User/Homepage.html",{"user":user})

def chat(request, id):
    message = tbl_chat.objects.filter((Q(reciver=id) | Q(reciver=id)) & (Q(sender=request.session["uid"]) | Q(sender=request.session["uid"])))
    return render(request,"User/Chat.html",{'reciver':id,'sender':request.session["uid"], 'message':message})