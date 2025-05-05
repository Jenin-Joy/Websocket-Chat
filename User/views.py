from django.shortcuts import render
from Guest.models import *
from User.models import *
from django.db.models import Q 

# Create your views here.

def homepage(request):
    user = tbl_user.objects.exclude(id=request.session["uid"])
    return render(request,"User/Homepage.html",{"user":user})

def chatold(request, id):
    message = tbl_chatold.objects.filter((Q(reciver=id) | Q(reciver=request.session["uid"])) & (Q(sender=id) | Q(sender=request.session["uid"])))
    return render(request,"User/ChatOld.html",{'reciver':id,'sender':request.session["uid"], 'message':message})