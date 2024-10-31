from rest_framework import serializers

from .models import Order, OrderProduct, RestaurantMenuItem, Restaurant

from geopoints.models import GeoPoint
from geopoints.geo_functions import get_order_restaurant_distance


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'firstname', 
            'lastname', 
            'phonenumber', 
            'address', 
            'products'
            ]

    def create(self, validated_data):
        new_order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )

        products_from_request = validated_data.pop('products')
        restaurant_ids = None

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

            menu_items = RestaurantMenuItem.objects.filter(product=product).values('restaurant_id')
            current_restaurant_ids = set(menu_item['restaurant_id'] for menu_item in menu_items)

            if restaurant_ids is None:
                restaurant_ids = current_restaurant_ids
            else:
                restaurant_ids &= current_restaurant_ids

        for restaurant_id in restaurant_ids:
            new_order.restaurants.add(Restaurant.objects.get(id=restaurant_id))

        geopoints = {geopoint.address: geopoint for geopoint in GeoPoint.objects.all()}

        for restaurant in new_order.restaurants:
            restaurant.distance = get_order_restaurant_distance(new_order, restaurant, geopoints)

        return new_order