from rest_framework import serializers
from .models import CartItem, Category, Ingredient, Pizza


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    pizza_count = serializers.SerializerMethodField()

    def get_pizza_count(self, obj):
        return obj.pizzas.count()


class IngredientSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    cssClass = serializers.CharField(source='css_class')

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'price', 'icon', 'cssClass']

    def get_price(self, obj):
        return float(obj.extra_price)


class PizzaSerializer(serializers.ModelSerializer):
    imageEmoji = serializers.CharField(source='image_emoji')
    defaultIngredientIds = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = ['id', 'name', 'description', 'imageEmoji', 'price', 'defaultIngredientIds']

    def get_defaultIngredientIds(self, obj):
        return list(obj.ingredients.values_list('id', flat=True))

    def get_price(self, obj):
        return float(obj.price)


class CartItemSerializer(serializers.ModelSerializer):
    pizzaId = serializers.IntegerField(source='pizza.id', read_only=True)
    pizzaName = serializers.CharField(source='pizza.name', read_only=True)
    imageEmoji = serializers.CharField(source='pizza.image_emoji', read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    unitPrice = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'pizzaId', 'pizzaName', 'crust', 'size', 'quantity', 'ingredients', 'imageEmoji', 'unitPrice']

    def get_unitPrice(self, obj):
        return float(obj.unit_price)


class CartItemWriteSerializer(serializers.Serializer):
    pizzaId = serializers.IntegerField()
    size = serializers.ChoiceField(choices=['small', 'medium', 'large'])
    crust = serializers.ChoiceField(choices=['classic', 'thin', 'cheese-burst'])
    ingredientIds = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)


class CartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)