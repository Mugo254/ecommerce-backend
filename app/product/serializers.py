from rest_framework import serializers
from .models import Category, Product, Order,ProductImages,ProductReviews
from django.contrib.sites.shortcuts import get_current_site

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category','description','price', 'created_at', 'updated_at']
        
class ProductImagesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImages
        fields = ['id', 'product', 'image', 'created_at', 'updated_at']
        
    def get_image(self, obj):
        request = self.context.get('request')
        scheme = 'https://' if request.is_secure() else 'http://'
        current_site = get_current_site(request).domain
        image_url = obj.image.url
        return f'{scheme}{current_site}{image_url}'
        
class ProductReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviews
        fields =  ['id', 'product', 'stars', 'description', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity','total_price', 'created_at', 'updated_at']