from rest_framework import viewsets,filters,permissions,status
from .models import Category, Product, Order, ProductImages, ProductReviews
from .serializers import CategorySerializer, ProductImagesSerializer, ProductReviewsSerializer, ProductSerializer, OrderSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site



class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny,]
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    lookup_field = "id"
    # http_method_names = ['get','post','delete','patch']

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    lookup_field = "id"

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product']
    lookup_field = "id"
    
class ProductImagesViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImagesSerializer
    permission_classes = [permissions.IsAuthenticated,]
    queryset = ProductImages.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product']
    lookup_field = "id"
    
class ProductReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewsSerializer
    permission_classes = [permissions.IsAuthenticated,]
    queryset = ProductReviews.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product']
    lookup_field = "id"
    
class CombinedProductDetailsView(APIView):
    permission_classes = [permissions.AllowAny,]
    
    def get(self, request, *args, **kwargs):
        
        # Prefetch related images and reviews for all products so as not to make separate database queries for each product. This is will improve perfomance.
        products = Product.objects.prefetch_related('images', 'reviews').all()

        # Serialize each product with its images and reviews
        combined_items = [{
            "id": product.id,
            "name": product.name,
            "price":product.price,
            "description":product.description,
            "images": ProductImagesSerializer(product.images.all(), many=True,context={'request': request}).data,
            "reviews": ProductReviewsSerializer(product.reviews.all(), many=True).data,
        } for product in products]

        return Response({'products': combined_items}, status=status.HTTP_200_OK)
    
    
class ProductDetailsView(APIView):
    permission_classes = [permissions.AllowAny,]

    def get(self, request, pk, *args, **kwargs):
        
        
        try:
            # Fetch the product based on the provided ID (pk)
            product = Product.objects.prefetch_related('images', 'reviews').get(pk=pk)
        except Product.DoesNotExist:
            # Handle the case when the product with the provided ID does not exist
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the product along with its images and reviews
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "images": ProductImagesSerializer(product.images.all(), many=True,context={'request': request}).data,
            "reviews": ProductReviewsSerializer(product.reviews.all(), many=True).data,
        }

        # Return response with the product data
        return Response(product_data, status=status.HTTP_200_OK)
    
    
class ProductFilterView(APIView):
    def get(self, request):
        # Retrieve the search parameters from the request query parameters
        category = request.GET.get('category', 'all')
        search_query = request.GET.get('q', '')
        max_price = request.GET.get('price__current__value_lte', 'all')
        
        
        current_site = get_current_site(request).domain
        scheme = request.is_secure() and "https://" or "http://" 

        # Construct the queryset based on the search parameters
        queryset = Product.objects.all()

        if category != 'all':
            queryset = queryset.filter(category__name=category)

        if search_query:
            # Perform case-insensitive search across multiple fields using Q objects
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )

        if max_price != 'all':
            queryset = queryset.filter(price__lte=max_price)

        # Retrieve specific fields from the queryset
        products_data = []
        for product in queryset:
            # Fetch the image associated with the product
            product_image = ProductImages.objects.filter(product=product).first()
            image_url = product_image.image.url if product_image else None

            # Construct the product data dictionary
            product_data = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': f'{scheme}{current_site}{image_url}',
            }
            products_data.append(product_data)

        # Return the data in the response
        return Response(products_data)
    
class ProductSearchView(APIView):
    def get(self, request):
        search_query = request.GET.get('q', '')
        
        # Construct the queryset based on the search parameters
        queryset = Product.objects.all()
        
        current_site = get_current_site(request).domain
        scheme = request.is_secure() and "https://" or "http://" 

        # Retrieve specific fields from the queryset
        products_data = []
        
        if len(search_query) != 0:
            # Perform case-insensitive search across multiple fields using Q objects
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
            for product in queryset:
                # Fetch the image associated with the product
                product_image = ProductImages.objects.filter(product=product).first()
                image_url = product_image.image.url if product_image else None

                # Construct the product data dictionary
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': f'{scheme}{current_site}{image_url}',

                }
                products_data.append(product_data)
        
        else:
            products_data = []


        


        # Return the data in the response
        return Response(products_data)
    

