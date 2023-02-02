from django.urls import path
from . import views

urlpatterns = [
    path('groups/manager/users/', views.manager_list),
    path('groups/manager/users/<int:userId>', views.manager_detail),
]
