from django.urls import path
from . import views

urlpatterns = [
    path('groups/manager/users/', views.ManagerList.as_view()),
    path('groups/manager/users/<int:userId>', views.ManagerDetail.as_view()),
    path('groups/delivery-crew/users/', views.DeliveryCrewList.as_view()),
    path('groups/delivery-crew/users/<int:userId>', views.DeliveryCrewDetail.as_view()),
    path('menu-items', views.MenuItemsList.as_view()),
    path('menu-items/<int:id>', views.MenuItemsDetail.as_view()),
    path('cart/menu-items', views.CartList.as_view()),
    path('orders', views.OrdersList.as_view()),
    path('orders/<int:id>', views.OrdersDetail.as_view())
]
