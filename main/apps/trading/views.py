from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from apps.users.permissions import IsOwner, IsSalesman, IsAdmin
from apps.users.models import User

from .models import Order, Transaction
from .serializers import OrderSerializer, TransactionSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if self.request.user.role == User.ADMIN:
            return Order.objects.all()  
        return Order.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action == 'create':
            order_type = self.request.data.get('order_type')
            if order_type == Order.SELL:
                return [IsAuthenticated(), IsSalesman() | IsAdmin()]
        return [permission() for permission in self.permission_classes]
    
    def perform_create(self, serializer):
        with transaction.atomic():  
            order = serializer.save(user=self.request.user)
            Transaction.objects.create(order=order, total_amount=order.price * order.quantity)
            
class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == User.ADMIN:
            return Transaction.objects.all()  
        return Transaction.objects.filter(order__user=self.request.user)
