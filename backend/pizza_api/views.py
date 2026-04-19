from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Pizza, Order
from .serializers import PizzaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# (FBV)

@api_view(['GET'])
def pizza_list(request):
    """Получение всех available пицц """
    pizzas = Pizza.objects.available()
    serializer = PizzaSerializer(pizzas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def pizza_detail(request, pk):
    """Получение одной пиццы по ID"""
    try:
        pizza = Pizza.objects.get(pk=pk)
    except Pizza.DoesNotExist:
        return Response({'error': 'Pizza is not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PizzaSerializer(pizza)
    return Response(serializer.data)


# (CBV) 

class OrderListCreateView(APIView):
    """Класс для просмотра и создания заказов"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Показываем заказы только текущего пользователя
        orders = Order.objects.filter(user=request.user)
        return Response({"message": "Список ваших заказов"})

    def post(self, request):
        # Линк на request.user
        data = request.data
        order = Order.objects.create(user=request.user, total_price=data.get('total_price', 0))
        return Response({"id": order.id, "status": "Заказ создан"}, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    """CRUD: Удаление и обновление заказа """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)