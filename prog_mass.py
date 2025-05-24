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
    
    distance_m = distance_nm * 1852.0

    geoid = Geod(ellps="WGS84")

    azimuth, back_azimuth, total_distance = geoid.inv(lon1, lat1, lon2, lat2)

    ratio = distance_m / total_distance

    fl_interp = fl1 + ratio * (fl2 - fl1)

    lon_interp, lat_interp, _ = geoid.fwd(lon1, lat1, azimuth, distance_m)

    return lat_interp, lon_interp, fl_interp

def interpolate_by_mass(data, mass, fl):
    masses = sorted(map(int, data.keys()))

    lower_mass = max(m for m in masses if m <= mass)
    upper_mass = min(m for m in masses if m >= mass)

    if lower_mass == upper_mass:
        fl_values = np.array([int(item["fl"]) for item in data[str(lower_mass)]["0"]])
        fuel_values = np.array([float(item["fuel"]) for item in data[str(lower_mass)]["0"]])
        fuel_interp = interp1d(fl_values, fuel_values, kind="linear", fill_value="extrapolate")
        return fuel_interp(fl)

    fl_values_lower = np.array([int(item["fl"]) for item in data[str(lower_mass)]["0"]])
    fuel_values_lower = np.array([float(item["fuel"]) for item in data[str(lower_mass)]["0"]])
    fuel_interp_lower = interp1d(fl_values_lower, fuel_values_lower, kind="linear", fill_value="extrapolate")
    fuel_lower = fuel_interp_lower(fl)

    fl_values_upper = np.array([int(item["fl"]) for item in data[str(upper_mass)]["0"]])
    fuel_values_upper = np.array([float(item["fuel"]) for item in data[str(upper_mass)]["0"]])
    fuel_interp_upper = interp1d(fl_values_upper, fuel_values_upper, kind="linear", fill_value="extrapolate")
    fuel_upper = fuel_interp_upper(fl)

    fuel_interpolated = fuel_lower + (fuel_upper - fuel_lower) * (mass - lower_mass) / (upper_mass - lower_mass)

    return fuel_interpolated


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
            interpolated_fuel = interpolate_by_mass(json, mass, fl_end)
            fuel += interpolated_fuel
            break 

        

        fl_values = np.array([int(item["fl"]) for item in data])
        fuel_values = np.array([float(item["fuel"]) for item in data])
        fuel_interp = interp1d(fl_values, fuel_values, kind="linear", fill_value="extrapolate")

        interpolated_fuel = interpolate_by_mass(json, mass, result[2])

        if fl_next == fl_start:
            fuel = 0
            time = 0
            distance = 0
        else:
            fuel += interpolated_fuel
            time += interpolated_fuel
            distance += interpolated_fuel

        mass -= interpolated_fuel


        lat_next, lon_next, fl_next = result[0], result[1], result[2]
        # print(fuel, interpolated_fuel, result)

    print('Mass:',mass, 'Fuel:', fuel)

    



    

if __name__ == "__main__":
    main()
