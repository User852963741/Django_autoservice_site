from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cars/', views.cars, name='cars'),
    path('services/', views.services, name='services'),
    path('contacts/', views.contacts, name='contacts'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('orders/<int:order_id>', views.order, name='order'),
    path('cars/<int:car_id>', views.car, name='car'),
    path('myorders/', views.OrdersByUserListView.as_view(), name='my_orders')

]