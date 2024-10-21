from rest_framework.serializers import ModelSerializer, ListField

from .models import Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']



class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True)
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
        products_from_request = validated_data.pop('products')
        for product_data in products_from_request:
            product = product_data['product']
            quantity = product_data['quantity']
            price = product.price * quantity
            OrderProduct.objects.create(
                order=new_order,
                product=product,
                quantity=quantity,
                price=price
            )
        return new_order
    