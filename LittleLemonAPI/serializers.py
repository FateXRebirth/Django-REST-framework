from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Cart, Order, OrderItem

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']
        
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    user = ManagerSerializer(read_only=True)
    # delivery_crew = ManagerSerializer(required=False, allow_null=True)
    # status = serializers.BooleanField(required=False)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)
    order_item = OrderItemSerializer(read_only=True, many=True)
    
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date', 'order_item']