from django.contrib import admin
from .models import SalesOrder, Invoice, Discount

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'product__name']

@admin.register(Invoice) 
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'sales_order', 'invoice_date']
    list_filter = ['invoice_date']
    search_fields = ['sales_order__user__username']

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['code', 'percentage', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['valid_from', 'valid_to']
    search_fields = ['code']
