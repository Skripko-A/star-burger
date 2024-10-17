from rest_framework.serializers import ModelSerializer, ListField

from .models import Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderProductSerializer(), allow_empty=False, write_only=True)
    class Meta:
        model = Order
        fields = ['firstname','lastname', 'phonenumber', 'address', 'products']
        