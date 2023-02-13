from django.urls import path
from . import views

urlpatterns = [
    path('groups/manager/users/', views.manager_list),
    path('groups/manager/users/<int:userId>', views.manager_detail),
    path('groups/delivery-crew/users/', views.delivery_crew_list),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_crew_detail),
    path('menu-items', views.MenuItemsList.as_view()),
    path('menu-items/<int:id>', views.MenuItemsDetail.as_view()),
    path('cart/menu-items', views.CartList.as_view()),
    path('orders', views.OrdersList.as_view())
]
