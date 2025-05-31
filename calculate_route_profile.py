import json
import math
import requests
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def calculate_route_segments(route_points):
    """
    Функція обчислює довжини відрізків маршруту та різниці висот між послідовними точками.
    Приймає список ідентифікаторів точок маршруту (рядки), шукає їх координати та висоту
    у файлах airports_esp.json та vertices_esp.json. Повертає список словників з інформацією
    про кожен відрізок маршруту.
    """
    # Завантажуємо дані аеропортів та вершин
    with open(resource_path('src/airports_esp.json'), 'r', encoding='utf-8') as f:
        airports_data = json.load(f)
    with open(resource_path('src/vertices_esp.json'), 'r', encoding='utf-8') as f:
        vertices_data = json.load(f)

    route_points = route_points.split()
    # Перетворюємо списки на словники за ключем 'ident' для швидкого пошуку
    airports = {entry['ident']: entry for entry in airports_data}
    vertices = {entry['ident']: entry for entry in vertices_data}

    # Допоміжний список для збереження (ident, lat, lon, alt)
    points = []
    for ident in route_points:
        if ident in airports:
            data = airports[ident]
            lat = data.get('latitude')
            lon = data.get('longitude')
            alt = data.get('altitude')
            if lat is None or lon is None or alt is None:
                raise ValueError(f"Недостатньо даних для точки {ident} в airports_esp.json")
            points.append((ident, lat, lon, alt))
        elif ident in vertices:
            data = vertices[ident]
            lat = data.get('latitude')
            lon = data.get('longitude')
            if lat is None or lon is None:
                raise ValueError(f"Недостатньо даних для точки {ident} в vertices_esp.json")
            alt = 0
            points.append((ident, lat, lon, alt))
        else:
            raise ValueError(f"Точка {ident} не знайдена у файлах даних")

    distance_km = 0
    altitude_fl_start = 0
    altitude_fl_end = 0

    for i in range(len(points) - 1):
        ident1, lat1, lon1, alt1 = points[i]
        ident2, lat2, lon2, alt2 = points[i + 1]
        # Конвертація координат з градусів в радіани
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        # Обчислюємо гаверсинус
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        earth_radius_km = 6371.0  # Радіус Землі в км
        distance = earth_radius_km * c
        if alt1:
            altitude_fl_start = alt1 / 1000 * 32.808
        elif alt2:
            altitude_fl_end = alt2 / 1000 * 32.808

        distance_km += distance

    return distance_km, altitude_fl_start, altitude_fl_end
