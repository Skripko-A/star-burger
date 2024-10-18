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
    new_order = order_serializer.save()

    products_from_request = request.data['products']
    for product_data in products_from_request:
        order_product_serializer = OrderProductSerializer(data=product_data)
        order_product_serializer.is_valid()
        order_product_serializer.validated_data['new_order'] = new_order
    try:
        order_product_serializer.save()
    except IntegrityError as e:
        print(f'Error during order create: {e}')
        return Response({'error': 'Error creating order products'}, status=400)
    

    return Response(order_serializer.data, status=201)
