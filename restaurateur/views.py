from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, views as auth_views
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import View



from foodcartapp.models import Product, Restaurant, Order
from geopoints.models import GeoPoint
from geopoints.geo_functions import get_order_restaurant_distance

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = Order.objects.with_price().exclude(status='A').order_by('status').prefetch_related('products__product')
    
    restaurants = Restaurant.objects.all()

    geopoints = {geopoint.address: geopoint for geopoint in GeoPoint.objects.filter(
        Q(
            address__in=order_items.values_list('address')
            )
             | 
        Q(
            address__in=restaurants.values_list('address')
            ))}

    orders_with_restaurants = {}

    for order in order_items:
        order_product_ids = []
        for order_product in order.products.all():
             order_product_ids.append(order_product.product.id)

        required_count = len(order_product_ids)

        order_restaurants = restaurants.annotate(
            product_count=Count(
                'menu_items__product', filter=Q(menu_items__product__id__in=order_product_ids)
                )
            ).filter(product_count=required_count)
        
        restaurants_list = []
        for restaurant in order_restaurants:
            restaurant.distance = get_order_restaurant_distance(order, restaurant, geopoints)
            restaurants_list.append(restaurant)
            restaurants_list.sort(key=lambda x: x.distance)
        
        orders_with_restaurants[order] = restaurants_list


    return render(
        request, 
        template_name='order_items.html', 
        context={
            'orders_with_restaurants': orders_with_restaurants
        }
    )
