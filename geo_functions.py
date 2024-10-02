import logging
import os

from geopy import distance
import requests


from environs import Env


logging.basicConfig(
    filename='geocoder.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


logging.debug('Это отладочное сообщение')
logging.info('Это информационное сообщение')
logging.warning('Это предупреждающее сообщение')
logging.error('Это сообщение об ошибке')
logging.critical('Это критическое сообщение')

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
        logging.error('Ошибка содеинения при попытке связи с api yandex geocoder')
    except requests.exceptions.HTTPError(403):
        logging.error('Проверьте токен доступа к api yandex geocoder')
    except requests.exceptions.TooManyRedirects:
        logging.error('Превышено количество запросов к api yandex geocoder')
    except requests.exceptions.ReadTimeout:
        logging.error('Превышено время ожидания ответа api yandex geocoder')
    except requests.exceptions.Timeout:
        logging.error('Превышено время ожидания ответа api yandex geocoder')
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

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
        restraunt_distance = distance.distance(order_coordinates, restaurant_coordinates).km
        restaurants_and_distances[restraunt_distance] = restaurant

    min_distance = min(restaurants_and_distances.keys())
    return restaurants_and_distances[min_distance]


def get_order_restaurant_distance(order, restaurant_address):
    order_coordinates = fetch_coordinates(order.address)
    restaurant_coordinates = fetch_coordinates(restaurant_address)
    return f'{distance.distance(order_coordinates, restaurant_coordinates).km:.3f} км'