from rest_framework.serializers import ModelSerializer, ListField

from .models import Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']
    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']
        price = product.price * quantity
        return OrderProduct.objects.create(
            order=Order.objects.get(id=validated_data['new_order'].id),
            product=product,
            quantity=quantity,
            price=price
        )


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderProductSerializer(), allow_empty=False, write_only=True)
    class Meta:
        model = Order
        fields = ['firstname','lastname', 'phonenumber', 'address', 'products']
    def create(self, validated_data):
        new_order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        return new_order
    