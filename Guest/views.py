from django.shortcuts import render,redirect
from Guest.models import *
# Create your views here.

def userreg(request):
    if request.method == "POST":
        tbl_user.objects.create(user_name=request.POST.get("txt_name"),user_contact=request.POST.get("txt_contact"),user_email=request.POST.get("txt_email"),user_password=request.POST.get("txt_password"))
        return render(request,"Guest/User.html",{"msg":"Registred Sucessfully"})
    else:
        return render(request,"Guest/User.html")   

def login(request):
    if request.method == "POST":
        usercount = tbl_user.objects.filter(user_email=request.POST.get("txt_email"),user_password=request.POST.get("txt_password")).count()
        if usercount > 0:
            user = tbl_user.objects.get(user_email=request.POST.get("txt_email"),user_password=request.POST.get("txt_password"))
            request.session["uid"] = user.id
            request.session["uname"] = user.user_name
            return redirect("User:homepage")
        else:
            return render(request,"Guest/Login.html",{"msg":"Invalid Email Or Password"})
    else:
        return render(request,"Guest/Login.html")