from django.contrib import admin
from .models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user'] # Removed status and created_at since they don't exist on Order model
    search_fields = ['user__username']

@admin.register(Transaction) 
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order'] # Removed amount and created_at since they don't exist on Transaction model
    search_fields = ['order__user__username']
