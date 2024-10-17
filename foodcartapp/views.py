from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer, OrderProductSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@csrf_exempt
@transaction.atomic
def register_order(request):
    '''
    Данные для тестирования:
    {"products": [{"product": 1, "quantity": 1}], 
    "firstname": "Василий", 
    "lastname": "Васильевич", 
    "phonenumber": "+79123456789", 
    "address": "Лондон"}
    '''
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.is_valid(raise_exception=True)
    new_order = Order.objects.create(
        firstname=order_serializer.validated_data['firstname'],
        lastname=order_serializer.validated_data['lastname'],
        phonenumber=order_serializer.validated_data['phonenumber'],
        address=order_serializer.validated_data['address']
        )
    
    order_products_fields = request.data['products']
    order_products = []

    for fields in order_products_fields:
        order_product_serializer = OrderProductSerializer(data=fields)
        order_product_serializer.is_valid(raise_exception=True)
        product = order_product_serializer.validated_data['product']
        quantity = order_product_serializer.validated_data['quantity']
        price = product.price * quantity
        order_product = OrderProduct(
            order=new_order,
            price=price,
            product=product,
            quantity=quantity
        )
        order_products.append(order_product)

    try:
        OrderProduct.objects.bulk_create(order_products)
    except IntegrityError as e:
        print(f'Error during bulk_create: {e}')
        return Response({'error': 'Error creating order products'}, status=400)
    

    return Response(order_serializer.data, status=201)
