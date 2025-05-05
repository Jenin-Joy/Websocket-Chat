from django.urls import path
from Chatapp import views
app_name = 'Chatapp'

urlpatterns = [
    path('chat/<int:id>',views.chat,name="chat"),
]