from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    extra_price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    icon = models.CharField(max_length=10, default='●')
    css_class = models.CharField(max_length=50, default='ingredient')

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_emoji = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='pizzas')
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    is_active = models.BooleanField(default=True)

    class PizzaManager(models.Manager):
        def available(self):
            return self.filter(is_active=True)

    objects = PizzaManager()

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('PR', 'Preparing'),
        ('SH', 'Shipping'),
        ('DE', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PR')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name}"


class CartItem(models.Model):
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    CRUST_CHOICES = [
        ('classic', 'Classic'),
        ('thin', 'Thin'),
        ('cheese-burst', 'Cheese burst'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='cart_items')
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='medium')
    crust = models.CharField(max_length=20, choices=CRUST_CHOICES, default='classic')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def unit_price(self):
        ingredient_total = sum((ingredient.extra_price for ingredient in self.ingredients.all()), Decimal('0.00'))
        size_extra = {
            'small': Decimal('-1.00'),
            'medium': Decimal('0.00'),
            'large': Decimal('2.00'),
        }[self.size]
        crust_extra = {
            'classic': Decimal('0.00'),
            'thin': Decimal('1.00'),
            'cheese-burst': Decimal('3.00'),
        }[self.crust]
        return self.pizza.price + ingredient_total + size_extra + crust_extra

    def __str__(self):
        return f"{self.user.username} - {self.pizza.name}"
