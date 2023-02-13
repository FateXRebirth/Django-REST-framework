from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import MenuItem, Cart, Order, OrderItem

class ManagerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']
        
class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(ModelSerializer):
    order_item = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date', 'order_item']