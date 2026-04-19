from django.contrib import admin
from .models import Pizza, Category, Ingredient, Order

admin.site.register(Pizza)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Order)