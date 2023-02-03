from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.models import User, Group
from .serializers import ManagerSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET', 'POST'])
def manager_list(request):
    if request.method == 'GET':
        managers = []
        for user in User.objects.all():
            if user.groups.filter(name="Manager").exists():            
                serializer = ManagerSerializer(user)
                managers.append(serializer.data)
        return Response(managers)
    elif request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({ "message": "user added to the manager group" }, status=status.HTTP_201_CREATED)
        return Response({ "message": "error" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({ "message": "method not allowed" }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def manager_detail(request, userId):
    if request.method == 'DELETE':
        if userId:
            user = get_object_or_404(User, id=userId)
            managers = Group.objects.get(name="Manager")
            managers.user_set.remove(user)
            return Response({ "message": "user removed from the manager group" }, status=status.HTTP_200_OK)
        return Response({ "message": "error" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({ "message": "method not allowed" }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@api_view(['GET', 'POST'])
def delivery_crew_list(request):
    if request.method == 'GET':
        delivery_crew = []
        for user in User.objects.all():
            if user.groups.filter(name="Delivery Crew").exists():            
                serializer = ManagerSerializer(user)
                delivery_crew.append(serializer.data)
        return Response(delivery_crew)
    elif request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery Crew")
            delivery_crew.user_set.add(user)
            return Response({ "message": "user added to the delivery crew group" }, status=status.HTTP_201_CREATED)
        return Response({ "message": "error" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({ "message": "method not allowed" }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def delivery_crew_detail(request, userId):
    if request.method == 'DELETE':
        if userId:
            user = get_object_or_404(User, id=userId)
            delivery_crew = Group.objects.get(name="Delivery Crew")
            delivery_crew.user_set.remove(user)
            return Response({ "message": "user removed from the delivery crew group" }, status=status.HTTP_200_OK)
        return Response({ "message": "error" }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({ "message": "method not allowed" }, status=status.HTTP_405_METHOD_NOT_ALLOWED)