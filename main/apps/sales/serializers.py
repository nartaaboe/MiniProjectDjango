from rest_framework import serializers

from .models import SalesOrder, Invoice, Discount

class SalesOrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = SalesOrder
        fields = ['id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'sales_order', 'invoice_date', 'pdf_file']

class DiscountSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = ['id', 'code', 'percentage', 'valid_from', 'valid_to', 'is_active']

    def get_is_active(self, obj):
        return obj.is_active
