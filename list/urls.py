from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    # login/logout
    path('auth/', include('rest_framework.urls')),
    # show all organizations
    path('user/org/all/', OrgListView.as_view()),
    # create new org with request.user as owner
    path('user/org/create/', OrgCreateView.as_view()),
    # mod if owner
    path('user/org/mod/<int:pk>/', OrgModView.as_view()),

    path('user/request/send/', JoinReqCreateView.as_view())

    # path('user/org/<int:pk>/leave/', ),
    # path('user/org/<int:pk>/invite/', ),
    # path('user/org/<int:pk>/requests/', ),
    # path('user/org/request/<int:pk>/accept', ),
    # path('user/org/request/<int:pk>/reject', ),

    # path('user/req/all/', ),
    # path('user/req/create/', ),
    # path('user/req/del/<int:pk>/', ),

    # path('user/passwords/show/', ),
    # path('user/passwords/mod/<int:pk>/', ),
    #
    # path('user/org/<int:pk>/todolists/show', ),
    # path('user/org/<int:pk>/todolists/create', ),
    # path('user/org/todolists/mod/<int:pk>/', ),
    # path('user/org/todolist/<int:pk>/tasks', ),
    # path('user/org/todolist/<int:pk>/tasks/add', ),
    # path('user/org/todolist/tasks/mod/<int:pk>', ),
]
