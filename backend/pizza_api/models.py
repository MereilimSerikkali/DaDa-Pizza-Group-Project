from django.db import models
from django.contrib.auth.models import User

# 1. Категории с иконками
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, null=True) # Для красивых URL

    def __str__(self):
        return self.name

# 2. Ингредиенты (для кастомизации)
class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    extra_price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

# 3. Сама Пицца
class Pizza(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_emoji = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='pizzas')
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    is_active = models.BooleanField(default=True) # Чтобы можно было "скрывать" позиции

    # Тот самый Custom Model Manager (Пункт 2 требований)
    # Позволяет делать Pizza.objects.available()
    class PizzaManager(models.Manager):
        def available(self):
            return self.filter(is_active=True)

    objects = PizzaManager() 

    def __str__(self):
        return self.name

# 4. Заказ (Сложная структура)
class Order(models.Model):
    STATUS_CHOICES = [
        ('PR', 'Preparing'),
        ('SH', 'Shipping'),
        ('DE', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PR')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

# 5. Промежуточная таблица 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)