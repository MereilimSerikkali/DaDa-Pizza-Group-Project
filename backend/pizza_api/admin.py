from django.contrib import admin

from .models import CartItem, Category, Ingredient, Order, OrderItem, Pizza


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'extra_price', 'icon', 'css_class')
    search_fields = ('name',)


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('ingredients',)
    list_editable = ('price', 'is_active')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    inlines = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pizza', 'size', 'crust', 'quantity', 'created_at')
    list_filter = ('size', 'crust', 'created_at')
    search_fields = ('user__username', 'pizza__name')
