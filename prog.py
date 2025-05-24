import numpy as np
from scipy.interpolate import interp1d
from pyproj import Geod


def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено. Створимо новий файл.")
        return {}
    except json.JSONDecodeError:
        print("Помилка читання JSON. Файл може бути пошкоджений.")
        return {}

def find_point_along_projection(lat1, lon1, fl1, lat2, lon2, fl2, distance_nm):
    # Конвертуємо морські милі у метри
    distance_m = distance_nm * 1852.0

    # Створюємо об'єкт Geod для геоїда WGS-84
    geoid = Geod(ellps="WGS84")

    # Обчислюємо повну відстань між початковою та кінцевою точками
    azimuth, back_azimuth, total_distance = geoid.inv(lon1, lat1, lon2, lat2)

    # Відносний коефіцієнт (частка шляху)
    ratio = distance_m / total_distance

    # Інтерполяція висоти
    fl_interp = fl1 + ratio * (fl2 - fl1)

    # Знаходимо нову точку на відстані distance_m уздовж проєкції
    lon_interp, lat_interp, _ = geoid.fwd(lon1, lat1, azimuth, distance_m)

    return lat_interp, lon_interp, fl_interp




def main():
    file_path = "src/boeing-738-climb.json"
    json = load_json(file_path)

    mass = 60000

    data = json[str(mass)]['0']


    lat_start, lon_start = 2.078333333, 41.29694444
    lat_end, lon_end = 1.0030555555556, 40.549722222222

    fl_start = 140
    fl_end = 333

    distance_nm = 5







    lat1, lon1, fl1 = lat_start, lon_start, fl_start  # Початкова точка (широта, довгота, FL)
    lat2, lon2, fl2 = lat_end, lon_end, fl_end   # Кінцева точка (широта, довгота, FL)


    # result = find_point_along_projection(lat1, lon1, fl1, lat2, lon2, fl2, distance_nm)
    # print(f"Точка на відстані {distance_nm} морських миль:")
    # print(f"- Широта: {result[0]:.6f}")
    # print(f"- Довгота: {result[1]:.6f}")
    # print(f"- Висота (FL): {result[2]:.2f}")


    isa = '0'
    fuel = 0
    time = 0
    distance = 0

    interpolated_fuel = 0

    lat_next = None
    lon_next = None
    fl_next = None

    while True:

        

        if not lat_next and not lon_next and not fl_next:
            lat_next = lat_start
            lon_next = lon_start
            fl_next = fl_start

        lat1, lon1, fl1 = lat_next, lon_next, fl_next
        lat2, lon2, fl2 = lat_end, lon_end, fl_end 
        result = find_point_along_projection(lat1, lon1, fl1, lat2, lon_end, fl2, distance_nm)



        if result and result[2] >= fl_end:
            interpolated_fuel = fuel_interp(fl_end)
            fuel += interpolated_fuel
            print(interpolated_fuel)
            break 

        

        

        fl_values = np.array([int(item["fl"]) for item in data])
        fuel_values = np.array([float(item["fuel"]) for item in data])
        fuel_interp = interp1d(fl_values, fuel_values, kind="linear", fill_value="extrapolate")

        interpolated_fuel = fuel_interp(result[2])

        if fl_next == fl_start:
            fuel = 0
        else:
            fuel += interpolated_fuel

        lat_next, lon_next, fl_next = result[0], result[1], result[2]

        print(fuel, interpolated_fuel, result)
        
    print(fuel)
    

    









    # print(fuel)


    # mass = int(list(json.keys())[0])
    # mass_str = list(json.keys())[0]

    # for f in range(fl_start,fl_end):
    #     for elem in json[mass_str][isa]:
    #         interpolated_distance = distance_interp(f)
            
    #         interpolated_tas = tas_interp(f)

    #         print(interpolated_fuel)

            
    #         time += int(elem['time'])
    #         distance += interpolated_distance

    # fl_values = np.array([int(item["fl"]) for item in data])
    # distance_values = np.array([float(item["distance"]) for item in data])
    # fuel_values = np.array([float(item["fuel"]) for item in data])
    # tas_values = np.array([float(item["tas"]) for item in data])

    # distance_interp = interp1d(fl_values, distance_values, kind="linear", fill_value="extrapolate")
    # fuel_interp = interp1d(fl_values, fuel_values, kind="linear", fill_value="extrapolate")
    # tas_interp = interp1d(fl_values, tas_values, kind="linear", fill_value="extrapolate")





    

    




    

if __name__ == "__main__":
    main()
