# urls.py
from django.urls import path,include,re_path
from django.conf import settings
from .views import CategoryViewSet, ProductDetailsView, ProductFilterView, ProductReviews,ProductImagesViewSet, OrderViewSet,CombinedProductDetailsView, ProductReviewsViewSet, ProductSearchView
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()
    
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'product-reviews', ProductReviewsViewSet, basename='product-reviews')
router.register(r'product-images', ProductImagesViewSet, basename='product-images')
router.register(r'orders', OrderViewSet, basename='orders')
    
urlpatterns = [
    re_path(r'^', include((router.urls))), 
    
    path('products/', CombinedProductDetailsView.as_view(), name='products'),
    path('product/<int:pk>/', ProductDetailsView.as_view(), name='product-details'),
    path('product/filter/', ProductFilterView.as_view(), name='product-filter'),
    path('product/search/', ProductSearchView.as_view(), name='product-search'),
    

]