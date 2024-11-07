import logging

from environs import Env
from geopy import distance
import requests

from geopoints.models import GeoPoint


logging.basicConfig(
    filename='geocoder.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

env = Env()
env.read_env()


def fetch_coordinates(address):
    apikey = env('YANDEX_GEOCODER_API_KEY')
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": f"Moscow {address}",
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        logging.error('Ошибка содеинения при попытке связи с yandex geocoder')
    except requests.exceptions.HTTPError(403):
        logging.error('Проверьте токен доступа к yandex geocoder')
    except requests.exceptions.TooManyRedirects:
        logging.error('Превышено количество запросов к yandex geocoder')
    except requests.exceptions.ReadTimeout:
        logging.error('Превышено время ожидания ответа yandex geocoder')
    except requests.exceptions.Timeout:
        logging.error('Превышено время ожидания ответа yandex geocoder')
    found_places = response.json()
    ['response']
    ['GeoObjectCollection']
    ['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def find_nearest_restaurant(order):
    order_coordinates = fetch_coordinates(order.address)
    restaurants_and_distances = {}

    for restaurant in order.get_restaurants():
        restaurant_coordinates = fetch_coordinates(restaurant.address)
        restraunt_distance = distance.distance(
            order_coordinates, restaurant_coordinates
            ).km
        restaurants_and_distances[restraunt_distance] = restaurant

    min_distance = min(restaurants_and_distances.keys())
    return restaurants_and_distances[min_distance]


def get_geopoint(address, geopoints):
    geopoint = geopoints.get(address)
    if not geopoint:
        try:
            coordinates = fetch_coordinates(address)
            geopoint = GeoPoint.objects.create(
                lng=coordinates[0],
                lat=coordinates[1],
                address=address,
            )
            geopoint.save()
        except Exception as e:
            print(f"Ошибка получения координат для адреса {address}: {e}")
            return None
    return geopoint


def get_order_restaurant_distance(order, restaurant, geopoints):
    order_geopoint = get_geopoint(order.address, geopoints)
    restaurant_geopoint = get_geopoint(restaurant.address, geopoints)

    if order_geopoint is None or restaurant_geopoint is None:
        return "Не удалось получить координаты для одного из адресов."

    order_restaurant_distance = distance.distance(
        (order_geopoint.lng, order_geopoint.lat),
        (restaurant_geopoint.lng, restaurant_geopoint.lat)
    )
    return f'{order_restaurant_distance.km:.3f} км'
