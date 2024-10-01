from geopy import distance
import requests


def fetch_coordinates(address):
    #apikey = os.getenv('YANDEX_GEOCODER_API_KEY')
    apikey = 'd9c66e4b-6109-49a0-b8eb-b1ca46f938ab'
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": f"Moscow {address}",
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
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