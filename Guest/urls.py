from django.urls import path
from Guest import views
app_name = 'Guest'

urlpatterns = [
    path('userreg/',views.userreg,name="userreg"),
    path('',views.login,name="login"),
]