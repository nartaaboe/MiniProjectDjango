from rest_framework import viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings

from apps.users.permissions import IsAdmin, IsSalesman
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]  
        return [permissions.AllowAny()]  

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [
                permissions.IsAuthenticated(), 
                permissions.OR(
                    IsSalesman(),
                    IsAdmin()
                )
            ]  
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Search by name or description
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            )
        
        return queryset.order_by('-created_at')
    
    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Create a cache key based on the product ID
        cache_key = f'product_{kwargs["pk"]}'
        
        # Try to get the cached data
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If no cache exists, get the data and cache it
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, settings.CACHE_TTL)
        return response
        
    def perform_update(self, serializer):
        # Clear cache when product is updated
        instance = serializer.save()
        cache_key = f'product_{instance.pk}'
        cache.delete(cache_key)
        cache.delete('product_list')  # Clear the list cache as well
        
    def perform_destroy(self, instance):
        # Clear cache when product is deleted
        cache_key = f'product_{instance.pk}'
        cache.delete(cache_key)
        cache.delete('product_list')  # Clear the list cache as well
        super().perform_destroy(instance)
