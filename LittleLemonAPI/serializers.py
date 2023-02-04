from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import MenuItem

class ManagerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']
        
class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']