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
from datetime import date

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
    
@permission_classes([IsAuthenticated])
class ManagerList(APIView):

    @only_for([MANAGER_GROUP])
    def get(self, request, format=None):
        managers = []
        for user in get_list_or_404(User):
            if user.groups.filter(name=MANAGER_GROUP).exists():            
                serialized_item = UserSerializer(user)
                managers.append(serialized_item.data)
        return Response(managers, status=status.HTTP_200_OK)

    @only_for([MANAGER_GROUP])
    def post(self, request, format=None):
        try:
            username = request.data["username"]
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name=MANAGER_GROUP)
            managers.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
class ManagerDetail(APIView):

    @only_for([MANAGER_GROUP])
    def delete(self, request, userId, format=None):
        user = get_object_or_404(User, id=userId)
        managers = Group.objects.get(name=MANAGER_GROUP)
        managers.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
    
@permission_classes([IsAuthenticated])
class DeliveryCrewList(APIView):

    @only_for([MANAGER_GROUP])
    def get(self, request, format=None):
        delivery_crews = []
        for user in get_list_or_404(User):
            if user.groups.filter(name=DELIVERY_CREW_GROUP).exists():            
                serialized_item = UserSerializer(user)
                delivery_crews.append(serialized_item.data)
        return Response(delivery_crews, status=status.HTTP_200_OK)
    
    @only_for([MANAGER_GROUP])
    def post(self, request, format=None):
        try:
            username = request.data["username"]
            user = get_object_or_404(User, username=username)
            delivery_crews = Group.objects.get(name=DELIVERY_CREW_GROUP)
            delivery_crews.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
@permission_classes([IsAuthenticated])
class DeliveryCrewDetail(APIView):

    @only_for([MANAGER_GROUP])
    def delete(self, request, userId, format=None):
        user = get_object_or_404(User, id=userId)
        delivery_crews = Group.objects.get(name=DELIVERY_CREW_GROUP)
        delivery_crews.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)

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
        return Response(serialized_item.data, status=status.HTTP_200_OK)

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
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
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

@permission_classes([IsAuthenticated])
class CartList(APIView):

    @only_for([CUSTOMER_GROUP])
    def get(self, request, format=None):
        cart = get_list_or_404(Cart, user=request.user)
        serialized_item = CartSerializer(cart, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    @only_for([CUSTOMER_GROUP])
    def post(self, request, format=None):
        try:
            menu_item = get_object_or_404(MenuItem, id=request.data["menuitem"])
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
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @only_for([CUSTOMER_GROUP])
    def delete(self, request, format=None):
        for cart in get_list_or_404(Cart, user=request.user):
            cart.delete()
        return Response(status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
class OrdersList(APIView):
    
    @only_for([MANAGER_GROUP, DELIVERY_CREW_GROUP,  CUSTOMER_GROUP])
    def get(self, request, format=None):
        user_group = get_group(request.user)
        if user_group == MANAGER_GROUP:
            orders = get_list_or_404(Order)
        elif user_group == DELIVERY_CREW_GROUP:
            orders = get_list_or_404(Order, delivery_crew=request.user)
        else:
            orders = get_list_or_404(Order, user=request.user)
        serialized_item = OrderSerializer(orders, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    @only_for([CUSTOMER_GROUP])
    def post(self, request, format=None):
        order = Order(user=request.user, total=0, date=date.today())
        order.save()
        total = 0
        for item in get_list_or_404(Cart, user=request.user):
            order_item = OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            total += item.price
            order_item.save()
            item.delete()
        order = get_object_or_404(Order, id=order.id)
        order.total = total
        order.save(update_fields=['total'])
        serialized_item = OrderSerializer(order)
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)

@permission_classes([IsAuthenticated])
class OrdersDetail(APIView):
    
    @only_for([CUSTOMER_GROUP])
    def get(self, request, id, format=None):
        order = get_object_or_404(Order, id=id, user=request.user)
        serialized_item = OrderSerializer(order)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    @only_for([MANAGER_GROUP])
    def put(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        serialized_item = OrderSerializer(order, data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    @only_for([MANAGER_GROUP, DELIVERY_CREW_GROUP])
    def patch(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        user_group = get_group(request.user)
        data = {}
        if user_group == MANAGER_GROUP:
            data["delivery_crew"] = request.data["delivery_crew"]
            data["status"] = request.data["status"]
        if user_group == DELIVERY_CREW_GROUP:
            data["status"] = request.data["status"]
        serialized_item = OrderSerializer(order, data=data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    
    @only_for([MANAGER_GROUP])
    def delete(self, request, id, format=None):
        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response(status=status.HTTP_200_OK)