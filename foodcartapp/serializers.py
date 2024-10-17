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
    def create(self, validated_data):
        new_order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        products_from_request = validated_data.pop('products')
        order_products = []
        for product_data in products_from_request:
            product = product_data['product']
            quantity = product_data['quantity']
            price = product.price * quantity
            order_product = OrderProduct(
                order=new_order,
                product=product,
                quantity=quantity,
                price=price
            )
            order_products.append(order_product)

        OrderProduct.objects.bulk_create(order_products)

        return new_order