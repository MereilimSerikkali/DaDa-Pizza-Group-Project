from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CartItem, Category, Ingredient, Order, Pizza
from .serializers import (
    CartItemSerializer,
    CartItemWriteSerializer,
    CartQuantitySerializer,
    IngredientSerializer,
    PizzaSerializer,
)

User = get_user_model()

def ensure_demo_data():
    category, _ = Category.objects.get_or_create(name='Signature', defaults={'slug': 'signature'})

    ingredient_defaults = [
        ('Pepperoni', Decimal('1.50'), '●', 'pepperoni'),
        ('Mushrooms', Decimal('1.10'), '◔', 'mushroom'),
        ('Olives', Decimal('0.90'), '◉', 'olive'),
        ('Basil', Decimal('0.80'), '✦', 'basil'),
        ('Mozzarella', Decimal('1.30'), '✹', 'mozzarella'),
        ('Chicken', Decimal('1.70'), '◆', 'chicken'),
        ('Jalapeños', Decimal('1.00'), '✦', 'jalapeno'),
        ('Cherry Tomatoes', Decimal('1.00'), '●', 'tomato'),
    ]
    ingredients = {}
    for name, price, icon, css_class in ingredient_defaults:
        existing = Ingredient.objects.filter(name=name).order_by('id')

        if existing.exists():
            ingredient = existing.first()

            duplicates = existing.exclude(id=ingredient.id)
            if duplicates.exists():
                duplicates.delete()

            changed = False
            if ingredient.extra_price != price:
                ingredient.extra_price = price
                changed = True
            if ingredient.icon != icon:
                ingredient.icon = icon
                changed = True
            if ingredient.css_class != css_class:
                ingredient.css_class = css_class
                changed = True
            if changed:
                ingredient.save(update_fields=['extra_price', 'icon', 'css_class'])
        else:
            ingredient = Ingredient.objects.create(
                name=name,
                extra_price=price,
                icon=icon,
                css_class=css_class,
            )

        ingredients[name] = ingredient

    pizza_defaults = [
        {
            'name': 'Royal Pepperoni',
            'description': 'Spicy pepperoni, mozzarella and tomato sauce.',
            'image_emoji': '🍕',
            'price': Decimal('12.90'),
            'ingredient_names': ['Pepperoni', 'Mozzarella'],
        },
        {
            'name': 'Forest Mushroom',
            'description': 'Creamy mushroom pizza with basil and mozzarella.',
            'image_emoji': '🍄',
            'price': Decimal('11.40'),
            'ingredient_names': ['Mushrooms', 'Basil', 'Mozzarella'],
        },
        {
            'name': 'Chicken Heat',
            'description': 'Chicken, jalapeños, tomatoes and rich cheese.',
            'image_emoji': '🌶️',
            'price': Decimal('13.80'),
            'ingredient_names': ['Chicken', 'Jalapeños', 'Cherry Tomatoes', 'Mozzarella'],
        },
    ]

    for payload in pizza_defaults:
        existing = Pizza.objects.filter(name=payload['name']).order_by('id')

        if existing.exists():
            pizza = existing.first()

            duplicates = existing.exclude(id=pizza.id)
            if duplicates.exists():
                duplicates.delete()

            changed = False
            if pizza.description != payload['description']:
                pizza.description = payload['description']
                changed = True
            if pizza.image_emoji != payload['image_emoji']:
                pizza.image_emoji = payload['image_emoji']
                changed = True
            if pizza.price != payload['price']:
                pizza.price = payload['price']
                changed = True
            if pizza.category_id != category.id:
                pizza.category = category
                changed = True
            if not pizza.is_active:
                pizza.is_active = True
                changed = True
            if changed:
                pizza.save()
        else:
            pizza = Pizza.objects.create(
                name=payload['name'],
                description=payload['description'],
                image_emoji=payload['image_emoji'],
                price=payload['price'],
                category=category,
                is_active=True,
            )

        pizza.ingredients.set([ingredients[name] for name in payload['ingredient_names']])

    demo_user, created = User.objects.get_or_create(
        username='demo@pizzeria.com',
        defaults={
            'email': 'demo@pizzeria.com',
            'first_name': 'DaDa',
            'last_name': 'Lover',
        },
    )
    if created or not demo_user.check_password('pizza123'):
        demo_user.set_password('pizza123')
        demo_user.save()


@api_view(['POST'])
def login_view(request):
    ensure_demo_data()
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    user = authenticate(username=email, password=password)
    if not user:
        return Response({'message': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'user': {
                'id': user.id,
                'fullName': user.get_full_name() or user.username,
                'email': user.email or user.username,
                'role': 'admin' if user.is_staff else 'customer',
            },
        }
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
def pizza_list(request):
    ensure_demo_data()
    pizzas = Pizza.objects.available().prefetch_related('ingredients')
    serializer = PizzaSerializer(pizzas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pizza_detail(request, pk):
    ensure_demo_data()
    try:
        pizza = Pizza.objects.prefetch_related('ingredients').get(pk=pk)
    except Pizza.DoesNotExist:
        return Response({'message': 'Pizza is not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PizzaSerializer(pizza)
    return Response(serializer.data)


@api_view(['GET'])
def ingredient_list(request):
    ensure_demo_data()
    ingredients = Ingredient.objects.all().order_by('id')
    serializer = IngredientSerializer(ingredients, many=True)
    return Response(serializer.data)


class CartListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user).select_related('pizza').prefetch_related('ingredients')
        return Response(CartItemSerializer(items, many=True).data)

    @transaction.atomic
    def post(self, request):
        serializer = CartItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            pizza = Pizza.objects.get(pk=data['pizzaId'], is_active=True)
        except Pizza.DoesNotExist:
            return Response({'message': 'Pizza not found.'}, status=status.HTTP_404_NOT_FOUND)

        item = CartItem.objects.create(
            user=request.user,
            pizza=pizza,
            size=data['size'],
            crust=data['crust'],
        )
        item.ingredients.set(Ingredient.objects.filter(id__in=data['ingredientIds']))
        item.refresh_from_db()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        deleted_count, _ = CartItem.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared.' if deleted_count else 'Cart is already empty.'})


class CartDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return CartItem.objects.filter(user=request.user, pk=pk).select_related('pizza').prefetch_related('ingredients').first()

    def put(self, request, pk):
        item = self.get_object(request, pk)
        if not item:
            return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item.quantity = serializer.validated_data['quantity']
        item.save(update_fields=['quantity'])
        return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_object(request, pk)
        if not item:
            return Response({'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({'message': 'Item removed from cart.'})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def bank_account_view(request):
    return Response(
        {
            'holder': request.user.get_full_name() or 'DaDa Lover',
            'balance': Decimal('250.00'),
            'currency': 'USD',
            'last4': '4242',
        }
    )

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def bank_charge_view(request):
    amount = Decimal(str(request.data.get('amount', '0')))
    if amount <= 0:
        return Response({'message': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            'message': 'Payment successful.',
            'receiptId': f'RCPT-{request.user.id}-{CartItem.objects.filter(user=request.user).count()}',
            'remainingBalance': Decimal('250.00') - amount,
        }
    )


class OrderListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response({'count': orders.count()})

    def post(self, request):
        order = Order.objects.create(user=request.user, total_price=request.data.get('total_price', 0))
        return Response({'id': order.id, 'status': 'Заказ создан'}, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


