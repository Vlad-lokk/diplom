import json
import math

def calculate_route_segments(route_points):
    """
    Функція обчислює довжини відрізків маршруту та різниці висот між послідовними точками.
    Приймає список ідентифікаторів точок маршруту (рядки), шукає їх координати та висоту
    у файлах airports_esp.json та vertices_esp.json. Повертає список словників з інформацією
    про кожен відрізок маршруту.
    """
    # Завантажуємо дані аеропортів та вершин
    with open('src/airports_esp.json', 'r', encoding='utf-8') as f:
        airports_data = json.load(f)
    with open('src/vertices_esp.json', 'r', encoding='utf-8') as f:
        vertices_data = json.load(f)

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
            # Точка не знайдена в жодному із файлів
            raise ValueError(f"Точка {ident} не знайдена у файлах даних")

    # Обчислюємо відстані та різниці висот між послідовними точками маршруту
    segments = []
    for i in range(len(points) - 1):
        ident1, lat1, lon1, alt1 = points[i]
        ident2, lat2, lon2, alt2 = points[i+1]
        # Конвертація координат з градусів в радіани
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        # Обчислюємо гаверсинус
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.asin(math.sqrt(a))
        earth_radius_km = 6371.0  # Радіус Землі в км
        distance_km = earth_radius_km * c
        distance_nm = distance_km / 1.852  # Переводимо км у морські милі
        if alt1:
            alt_diff = alt1
        elif alt2:
            alt_diff = alt2
        else:
            alt_diff = 0

        segments.append({
            'from': ident1,
            'to': ident2,
            'distance_nm': distance_nm,
            'altitude_diff_ft': alt_diff
        })
    return segments



route_str = "LEBL LOTOS TORDU DIKUT SOPET VLC SERRA ASTRO POBOS  XEBAR YES MAMIS  BAZAS VIBAS LEGA"
# LEBL,LOTOS,TORDU,DIKUT,SOPET,VLC,SERRA,ASTRO,POBOS,XEBAR,YES,MAMIS,BAZAS,VIBAS,LEGA
route_list = route_str.split()
segments = calculate_route_segments(route_list)
for seg in segments:
    print(seg)