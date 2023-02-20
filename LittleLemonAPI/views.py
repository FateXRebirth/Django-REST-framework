from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.paginator import Paginator, EmptyPage
from .serializers import UserSerializer, MenuItemSerializer, CartSerializer, OrderSerializer
from .models import MenuItem, Cart, Order, OrderItem
from datetime import datetime

MANAGER_GROUP = "Manager"
DELIVERY_CREW_GROUP = "Delivery Crew"
CUSTOMER_GROUP = "Customer"

def only_for(group):
    def decorator_only_for(func):
        def wrapper(*args,**kwargs):
            request = args[1]
            if MANAGER_GROUP in group and request.user.groups.filter(name=MANAGER_GROUP).exists():
                return func(*args,**kwargs)
            if DELIVERY_CREW_GROUP in group and request.user.groups.filter(name=DELIVERY_CREW_GROUP).exists():
                return func(*args,**kwargs)
            if CUSTOMER_GROUP in group:
                return func(*args,**kwargs)
            return Response(status=status.HTTP_403_FORBIDDEN)
        return wrapper
    return decorator_only_for

def get_group(user):
    if user.groups.filter(name=MANAGER_GROUP).exists():
        return MANAGER_GROUP    
    elif user.groups.filter(name=DELIVERY_CREW_GROUP).exists():       
        return DELIVERY_CREW_GROUP
    else:
        return CUSTOMER_GROUP
    
class ManagerList(APIView):
    def get(self, request, format=None):
        managers = []
        for user in User.objects.all():
            if user.groups.filter(name=MANAGER_GROUP).exists():            
                serialized_item = UserSerializer(user)
                managers.append(serialized_item.data)
        return Response(managers)

    def post(self, request, format=None):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name=MANAGER_GROUP)
            managers.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class ManagerDetail(APIView):
    def delete(self, request, userId, format=None):
        if userId:
            user = get_object_or_404(User, id=userId)
            managers = Group.objects.get(name=MANAGER_GROUP)
            managers.user_set.remove(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class DeliveryCrewList(APIView):
    def get(self, request, format=None):
        delivery_crew = []
        for user in User.objects.all():
            if user.groups.filter(name=DELIVERY_CREW_GROUP).exists():            
                serialized_item = UserSerializer(user)
                delivery_crew.append(serialized_item.data)
        return Response(delivery_crew)
    
    def post(self, request, format=None):
        username = request.data["username"]
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name=DELIVERY_CREW_GROUP)
            delivery_crew.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class DeliveryCrewDetail(APIView):
    def delete(self, request, userId, format=None):
        if userId:
            user = get_object_or_404(User, id=userId)
            delivery_crew = Group.objects.get(name=DELIVERY_CREW_GROUP)
            delivery_crew.user_set.remove(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class MenuItemsList(APIView):
    
    @only_for([MANAGER_GROUP, DELIVERY_CREW_GROUP, CUSTOMER_GROUP])
    def get(self, request, format=None):
        menu_items = MenuItem.objects.select_related("category").all()
        
        # category_name = request.query_params.get("category")
        # to_price = request.query_params.get("to_price")
        # search = request.query_params.get("search")
        # ordering = request.query_params.get("ordering")
        # perpage = request.query_params.get("perpage", default=2)
        # page = request.query_params.get("page", default=1)
        # if category_name:
        #     menu_items = menu_items.filter(category__title=category_name)
        # if to_price:
        #     menu_items = menu_items.filter(price__lte=to_price)
        # if search:
        #     menu_items = menu_items.filter(title__startswith=search)
        # if ordering:
        #     ordering_fields = ordering.split(",")
        #     menu_items = menu_items.order_by(*ordering_fields)
        # paginator = Paginator(menu_items, per_page=perpage)
        # try:
        #     menu_items = paginator.page(number=page)
        # except EmptyPage:
        #     menu_items = []
        
        serialized_item = MenuItemSerializer(menu_items, many=True)
        return Response(serialized_item.data)

    @only_for([MANAGER_GROUP])
    def post(self, request, format=None):
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)

@permission_classes([IsAuthenticated])
class MenuItemsDetail(APIView):

    @only_for([MANAGER_GROUP, DELIVERY_CREW_GROUP, CUSTOMER_GROUP])
    def get(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        serialized_item = MenuItemSerializer(menu_item)
        return Response(serialized_item.data)
    
    @only_for([MANAGER_GROUP])
    def put(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        serialized_item = MenuItemSerializer(menu_item, data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()            
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    @only_for([MANAGER_GROUP])
    def patch(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        serialized_item = MenuItemSerializer(menu_item, data=request.data, partial=True)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    @only_for([MANAGER_GROUP])
    def delete(self, request, id, format=None):
        menu_item = get_object_or_404(MenuItem, id=id)
        menu_item.delete()
        return Response(status=status.HTTP_200_OK)

class CartList(APIView):
    def get(self, request, format=None):
        cart = Cart.objects.filter(user=request.user)
        serialized_item = CartSerializer(cart, many=True)
        return Response(serialized_item.data)

    def post(self, request, format=None):
        menu_item_name = request.data["menuitem"]
        menu_item = MenuItem.objects.get(title=menu_item_name)
        data = {
            "user": request.user.id,
            "menuitem": menu_item.id,
            "quantity": request.data["quantity"],
            "unit_price": menu_item.price,
            "price": int(request.data["quantity"]) * menu_item.price
        }
        serialized_item = CartSerializer(data=data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()      
        return Response(serialized_item.validated_data, status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        for cart in get_list_or_404(Cart, user=request.user):
            cart.delete()
        return Response(status=status.HTTP_200_OK)

class OrdersList(APIView):
    def get(self, request, format=None):
        user_group = get_group(request.user)
        if user_group == MANAGER_GROUP:
            orders = Order.objects.all()
        elif user_group == DELIVERY_CREW_GROUP:
            orders = Order.objects.filter(delivery_crew=request.user)    
        else:
            orders = Order.objects.filter(user=request.user)
        serialized_item = OrderSerializer(orders, many=True)
        return Response(serialized_item.data)

    def post(self, request, format=None):
        user_group = get_group(request.user)
        if user_group == CUSTOMER_GROUP:
            order = Order(user=request.user, total=0, date=datetime.now())
            total = 0
            for item in Cart.objects.filter(user=request.user):
                order_item = OrderItem(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
                total += item.price
                order_item.save()
                item.delete()
            serialized_item = OrderSerializer(order, data={"total": total})
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.validated_data, status=status.HTTP_201_CREATED)
        else:
            return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)
        

class OrdersDetail(APIView):
    def get(self, request, id, format=None):
        user_group = get_group(request.user)
        if user_group == CUSTOMER_GROUP:
            order = Order.objects.get(id=id)
            serialized_item = OrderSerializer(order)
            return Response(serialized_item.data)
        else:
            return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)
      
    
    def put(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        user_group = get_group(request.user)
        print(user_group)
        data = {}
        if user_group == MANAGER_GROUP:
            data["delivery_crew"] = request.data["delivery_crew"]
            data["status"] = request.data["status"]
        elif user_group == DELIVERY_CREW_GROUP:
            data["status"] = request.data["status"]
        else:
            return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)
        serialized_item = OrderSerializer(order, data=data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        user_group = get_group(request.user)
        data = {}
        if user_group == MANAGER_GROUP:
            data["delivery_crew"] = request.data["delivery_crew"]
            data["status"] = request.data["status"]
        elif user_group == DELIVERY_CREW_GROUP:
            data["status"] = request.data["status"]
        else:
            return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)
        serialized_item = OrderSerializer(order, data=data, partial=True)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status=status.HTTP_200_OK)
    
    def delete(self, request, id, format=None):
        user_group = get_group(request.user)
        if user_group == MANAGER_GROUP:
            order = get_object_or_404(Order, id=id)
            order.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("Not allowed", status=status.HTTP_403_FORBIDDEN)