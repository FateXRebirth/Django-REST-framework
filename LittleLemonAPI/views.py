from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, get_list_or_404
from .serializers import ManagerSerializer, MenuItemSerializer, CartSerializer, OrderSerializer
from .models import MenuItem, Cart, Order, OrderItem
from datetime import datetime

def get_group(user):
    if user.groups.filter(name="Manager").exists():
        return 'Manager'    
    elif user.groups.filter(name="Delivery Crew").exists():       
        return 'Delivery Crew'
    else:
        return 'Customer'     

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

class MenuItemsList(APIView):
    def get(self, request, format=None):        
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": "new menu item added" }, status=status.HTTP_201_CREATED)
        return Response({ "errorMessages": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
    
class MenuItemsDetail(APIView):
    def get(self, request, id, format=None):
        menu_item = MenuItem.objects.get(id=id)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        serializer = MenuItemSerializer(menu_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({ "errorMessages": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        menu_item.delete()
        return Response(status=status.HTTP_200_OK)

class CartList(APIView):
    def get(self, request, format=None):
        cart = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        menu_item_name = request.data['menuitem']
        menu_item = MenuItem.objects.get(title=menu_item_name)
        data = {
            "user": request.user.id,
            "menuitem": menu_item.id,
            "quantity": request.data['quantity'],
            "unit_price": menu_item.price,
            "price": int(request.data['quantity']) * menu_item.price
            
        }
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "message": "new menu item added to cart" }, status=status.HTTP_201_CREATED)
        return Response({ "errorMessages": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        for cart in get_list_or_404(Cart, user=request.user):
            cart.delete()
        return Response(status=status.HTTP_200_OK)

class OrdersList(APIView):
    def get(self, request, format=None):
        user_group = get_group(request.user)
        if user_group == 'Manager':
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)    
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        order = Order(user=request.user, total=0, date=datetime.now())
        total = 0
        for item in Cart.objects.filter(user=request.user):
            order_item = OrderItem(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
            total += item.price
            order_item.save()
            item.delete()
        order.total = total
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrdersDetail(APIView):
    def get(self, request, id, format=None):
        order = Order.objects.get(id=id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def put(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        user_group = get_group(request.user)
        data = {}
        if user_group == 'Customer':
            data['delivery_crew'] = request.data['delivery_crew']
            data['status'] = request.data['status']
        serializer = OrderSerializer(order, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({ "errorMessages": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)