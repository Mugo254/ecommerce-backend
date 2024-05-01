from django.contrib import admin
from .models import Category, Product, Order, ProductImages, ProductReviews

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name","created_at")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price","created_at")
    list_filter = ("category",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity", "total_price","created_at")
    list_filter = ("product",)
    
@admin.register(ProductReviews)
class ProductReviewsAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "stars", "description","created_at")
    list_filter = ("product",)
    
@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image", "created_at")
    list_filter = ("product",)
    
