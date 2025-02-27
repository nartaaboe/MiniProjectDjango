from django.db import models
from django.conf import settings

class Order(models.Model):
    BUY = "buy"
    SELL = "sell"
    
    ORDER_TYPES = [
        (BUY, "Buy"),
        (SELL, "Sell"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="orders")
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} - {self.order_type} {self.quantity} {self.product.name}"

class Transaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="transaction")
    executed_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"Transaction for {self.order}"
