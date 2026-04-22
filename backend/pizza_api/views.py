from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
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


def _build_auth_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'fullName': user.get_full_name() or user.username,
            'email': user.email or user.username,
            'role': 'admin' if user.is_staff else 'customer',
        },
    }


from .seed import ensure_demo_data


@api_view(['POST'])
def register_view(request):
    ensure_demo_data()
    full_name = request.data.get('fullName', '').strip()
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=email).exists():
        return Response({'message': 'This email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    first_name, _, last_name = full_name.partition(' ')
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    return Response(_build_auth_response(user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    ensure_demo_data()
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    user = authenticate(username=email, password=password)
    if not user:
        return Response({'message': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(_build_auth_response(user))


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'message': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response({'message': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
def pizza_list(request):
    ensure_demo_data()
    pizzas = Pizza.objects.available().prefetch_related('ingredients').order_by('id')
    serializer = PizzaSerializer(pizzas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pizza_detail(request, pk):
    ensure_demo_data()
    try:
        pizza = Pizza.objects.prefetch_related('ingredients').get(pk=pk, is_active=True)
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def bank_account_view(request):
    return Response(
        {
            'holder': request.user.get_full_name() or 'DaDa Lover',
            'last4': '4242',
            'provider': 'Secure Card Payment',
        }
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def bank_charge_view(request):
    amount = Decimal(str(request.data.get('amount', '0')))
    if amount <= 0:
        return Response({'message': 'Amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            'message': 'Payment successful.',
            'receiptId': f'RCPT-{request.user.id}-{CartItem.objects.filter(user=request.user).count()}',
        }
    )


class OrderListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response({'count': orders.count()})

    def post(self, request):
        order = Order.objects.create(user=request.user, total_price=request.data.get('total_price', 0))
        return Response({'id': order.id, 'status': 'Заказ создан'}, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
