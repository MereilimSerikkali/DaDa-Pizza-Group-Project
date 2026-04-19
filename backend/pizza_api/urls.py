from django.urls import path
from .views import pizza_list, pizza_detail, OrderListCreateView, OrderDetailView

urlpatterns = [
    # Пути для функций
    path('pizzas/', pizza_list),
    path('pizzas/<int:pk>/', pizza_detail),
    
    # Пути для классов
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
]