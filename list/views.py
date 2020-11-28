from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .serializers import *


# DOES this really need comments?
class OrgCreateView(generics.CreateAPIView):
    serializer_class = OrgCreateSerializer


class OrgListView(generics.ListAPIView):
    serializer_class = OrgSerializer
    queryset = Organization.objects.all()
    permission_classes = (IsAuthenticated, )


class OrgModView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrgSerializer
    queryset = Organization.objects.all()
    permission_classes = (IsMemberOrForbid, )


class JoinReqCreateView(generics.CreateAPIView):
    serializer_class = JoinReqSerializer
