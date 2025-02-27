from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesOrderViewSet, InvoiceViewSet, DiscountViewSet

router = DefaultRouter()
router.register(r'sales', SalesOrderViewSet, basename="salesorder")
router.register(r'invoices', InvoiceViewSet, basename="invoice")
router.register(r'discounts', DiscountViewSet, basename="discount")

urlpatterns = [
    path('', include(router.urls)), 
]