from rest_framework import serializers
from .models import Pizza, Category

# 1. Обычный Serializer (Пункт 4а)
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    pizza_count = serializers.SerializerMethodField() # "Вычисляемое" поле

    def get_pizza_count(self, obj):
        return obj.pizzas.count()

# 2. ModelSerializer (Пункт 4б)
class PizzaSerializer(serializers.ModelSerializer):
    # Переименовывание для фронтенда 
    imageEmoji = serializers.CharField(source='image_emoji')
    
    class Meta:
        model = Pizza
        fields = ['id', 'name', 'description', 'imageEmoji', 'price', 'category']