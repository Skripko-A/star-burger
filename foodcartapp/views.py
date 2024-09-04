import json
import re
from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.templatetags.static import static
from pydantic import BaseModel, Field, PositiveInt, constr, ValidationError, ConfigDict, conlist

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Product, Order, OrderProduct


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
def register_order(request):
    class ProductSchema(BaseModel):
        product: PositiveInt
        quantity: PositiveInt

    class OrderSchema(BaseModel):
        products: conlist(item_type=dict, min_length=1) # type: ignore
        firstname: constr(min_length=1) # type: ignore
        lastname: constr(min_length=1) # type: ignore
        phonenumber: str = Field(pattern = r'^(?:\+7[1-9]\d{2}|8\d{2})[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}')
        address: constr(min_length=1) # type: ignore
        model_config = ConfigDict(extra="forbid")
    try:
        order = request.data
        OrderSchema(**order)
        for product in order['products']:
            ProductSchema(**product)
        new_order = Order.objects.create(firstname=order['firstname'],
                                         lastname=order['lastname'],
                                         phonenumber=order['phonenumber'],
                                         address=order['address'])
        for product in order['products']:
            OrderProduct.objects.create(order=new_order,
                                        product=Product.objects.get(id=product['product']),
                                        quantity=product['quantity'])
        return Response(status=status.HTTP_201_CREATED, headers={'result': 'Order created'})
    except ValidationError as error:
        error_messages = error.errors()
        for error in error_messages:
            print(error)
        errors = {error['loc'][0]: error['msg'] for error in error_messages}
        return Response(status=HTTP_400_BAD_REQUEST, headers={'error': errors})
    except ObjectDoesNotExist as not_exist_error:
        return Response(status=HTTP_400_BAD_REQUEST, headers={'error': not_exist_error})
