from django.urls import path

from .views import (
    CartDetailView,
    CartListCreateView,
    OrderDetailView,
    OrderListCreateView,
    bank_account_view,
    bank_charge_view,
    ingredient_list,
    login_view,
    logout_view,
    pizza_detail,
    pizza_list,
    register_view,
)

urlpatterns = [
    path('auth/register/', register_view),
    path('auth/login/', login_view),
    path('auth/logout/', logout_view),
    path('pizzas/', pizza_list),
    path('pizzas/<int:pk>/', pizza_detail),
    path('ingredients/', ingredient_list),
    path('cart/', CartListCreateView.as_view()),
    path('cart/<int:pk>/', CartDetailView.as_view()),
    path('bank/account/', bank_account_view),
    path('bank/charge/', bank_charge_view),
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
]
