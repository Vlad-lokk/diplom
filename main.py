import json
import tkinter as tk
from tkinter import ttk
from scipy.interpolate import RegularGridInterpolator
from PIL import Image, ImageTk
from calculate_route_profile import calculate_route_segments


class AdvancedFuelCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Розрахунок витрат палива Boeing 738")
        master.geometry("800x600")
        master.resizable(False, False)

        self.route_mapping = {
            "BARCELONA - GRANADA ARMILLA": "LEBL LOTOS TORDU DIKUT SOPET VLC SERRA ASTRO POBOS XEBAR YES MAMIS BAZAS VIBAS LEGA",
            "Second": "Другий маршрут...",
            "Свій": ""
        }

        self.create_widgets()
        self.setup_bindings()

    def setup_bindings(self):
        # Прив'язка обробника подій тільки до Combobox
        self.route_type.bind("<<ComboboxSelected>>", self.on_route_type_change)

    def on_route_type_change(self, event=None):
        """Обробник зміни вибору в Combobox"""
        selected = self.route_type.get()

        # Завжди активуємо поле перед змінами
        self.custom_route_entry.config(state='normal')
        self.custom_route_entry.delete(0, tk.END)

        if selected == "Свій":
            self.custom_route_entry.config(state='normal')
        else:
            # Вставляємо відповідний маршрут зі словника
            self.custom_route_entry.insert(0, self.route_mapping[selected])
            self.custom_route_entry.config(state='disabled')

    def create_widgets(self):
        # Створення фону
        try:
            self.bg_image = Image.open('src/background.png')
            self.bg_image = self.bg_image.resize((800, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas = tk.Canvas(self.master, width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except Exception as e:
            print(f"Помилка завантаження фону: {e}")
            self.canvas = tk.Canvas(self.master, width=800, height=600, bg='white')
            self.canvas.pack()

        # Основний фрейм для віджетів
        self.widget_frame = tk.Frame(self.canvas, bd=5, relief='ridge', bg='#f0f0f0')
        self.widget_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

        # Елементи інтерфейсу
        self.route_type_label = tk.Label(
            self.widget_frame,
            text="Маршрут:",
            bg='#f0f0f0'
        )
        self.route_type_label.pack(pady=5)

        self.route_type = ttk.Combobox(
            self.widget_frame,
            width=40,
            values=list(self.route_mapping.keys())
        )
        self.route_type.pack(pady=5)
        self.route_type.set("BARCELONA - GRANADA ARMILLA")

        self.custom_route_label = tk.Label(
            self.widget_frame,
            text="Ваш маршрут:",
            bg='#f0f0f0'
        )
        self.custom_route_label.pack(pady=5)

        self.custom_route_entry = tk.Entry(
            self.widget_frame,
            width=40,
            state="disabled"
        )
        self.custom_route_entry.pack(pady=5)

        # Інші елементи...
        self.height_label = tk.Label(
            self.widget_frame,
            text="Висота FL",
            bg='#f0f0f0'
        )
        self.height_label.pack(pady=5)

        self.height_entry = tk.Entry(self.widget_frame, width=20)
        self.height_entry.pack(pady=5)

        self.calculate_button = tk.Button(
            self.widget_frame,
            text="Розрахувати",
            command=self.calculate_cost
        )
        self.calculate_button.pack(pady=20)

        self.on_route_type_change()

    def _calculate_cost(self):
        try:
            self.calculate_cost()
        except ValueError:
            pass


    def calculate_cost(self):
        route = self.custom_route_entry.get()
        height_fl = self.height_entry.get()

        self.mass_kg = 65000
        distance_km, altitude_fl_start, altitude_fl_end = calculate_route_segments(route)

        with open('src/boeing-738-climb.json', 'r') as f:
            self.boeing_data_climb = json.load(f)

        fl = self.calculate_total_climb(altitude_fl_start, int(height_fl))


        print(height_fl, fl)
        print(distance_km, altitude_fl_start, altitude_fl_end)

    def calculate_climb(self,climb_data, fl_target):
        # Сортуємо точки за значенням FL

        climb_data = self.interpolate_mass()

        climb_data = climb_data['0']

        sorted_data = sorted(climb_data, key=lambda x: int(x['fl']))
        fls = [int(point['fl']) for point in sorted_data]

        # Обробка випадків, коли FL виходить за межі даних
        if fl_target <= fls[0]:
            # Повертаємо першу точку, якщо FL менше або дорівнює мінімальному
            lower_idx = upper_idx = 0
        elif fl_target >= fls[-1]:
            # Повертаємо останню точку, якщо FL більше або дорівнює максимальному
            lower_idx = upper_idx = len(fls) - 1
        else:
            # Знаходимо інтервал для інтерполяції
            for i in range(1, len(fls)):
                if fls[i] >= fl_target:
                    lower_idx = i - 1
                    upper_idx = i
                    break

        # Якщо FL точно співпадає з точкою, повертаємо її значення
        if fls[lower_idx] == fl_target or lower_idx == upper_idx:
            point = sorted_data[lower_idx]
            return {
                'time': float(point['time']),
                'distance': float(point['distance']),
                'fuel': float(point['fuel'])
            }
        else:
            # Лінійна інтерполяція між двома найближчими точками
            fl_low = fls[lower_idx]
            fl_high = fls[upper_idx]
            ratio = (fl_target - fl_low) / (fl_high - fl_low)

            lower_point = sorted_data[lower_idx]
            upper_point = sorted_data[upper_idx]

            # Інтерполяція значень
            time = float(lower_point['time']) + (
                        float(upper_point['time']) - float(lower_point['time'])) * ratio
            distance = float(lower_point['distance']) + (
                        float(upper_point['distance']) - float(lower_point['distance'])) * ratio
            fuel = float(lower_point['fuel']) + (
                        float(upper_point['fuel']) - float(lower_point['fuel'])) * ratio

            return {
                'time': round(time, 2),
                'distance': round(distance, 2),
                'fuel': round(fuel, 2)
            }

    def calculate_total_climb(self, fl_start, fl_end):

        climb_data = self.interpolate_mass()

        climb_data = climb_data['0']

        sorted_data = sorted(climb_data, key=lambda x: int(x['fl']))
        fls = [int(point['fl']) for point in sorted_data]

        # Перевіряємо, чи fl_end >= fl_start
        if fl_start > fl_end:
            fl_start, fl_end = fl_end, fl_start

        # Визначаємо всі FL у заданому діапазоні (включаючи межі)
        all_fls = sorted(list(set(fls + [fl_start, fl_end])))
        relevant_fls = [fl for fl in all_fls if fl_start <= fl <= fl_end]
        relevant_fls = sorted(relevant_fls)

        # Ініціалізуємо сумарні значення
        total_time = 0.0
        total_distance = 0.0
        total_fuel = 0.0

        # Обчислюємо різниці між послідовними точками
        for i in range(len(relevant_fls) - 1):
            current_fl = relevant_fls[i]
            next_fl = relevant_fls[i + 1]

            # Отримуємо дані для поточної та наступної висоти
            current_data = self.calculate_climb(climb_data, current_fl)
            next_data = self.calculate_climb(climb_data, next_fl)

            # Додаємо різницю до суми
            total_time += next_data['time'] - current_data['time']
            total_distance += next_data['distance'] - current_data['distance']
            total_fuel += next_data['fuel'] - current_data['fuel']
            self.mass_kg = self.mass_kg - (next_data['fuel'] - current_data['fuel'])


        return {
            'total_time': round(total_time, 2),
            'total_distance': round(total_distance, 2),
            'total_fuel': round(total_fuel, 2)
        }

    def interpolate_mass(self):

        target_mass = self.mass_kg
        aircraft_data = self.boeing_data_climb

        masses = sorted(aircraft_data.keys(), key=lambda x: int(x))
        target_mass_int = int(target_mass)

        # Знаходимо найближчі маси для інтерполяції
        lower_mass, upper_mass = None, None
        for i, mass in enumerate(masses):
            mass_int = int(mass)
            if mass_int == target_mass_int:
                return aircraft_data[mass]  # Якщо маса вже є у файлі
            if mass_int < target_mass_int:
                lower_mass = mass
            elif mass_int > target_mass_int and not upper_mass:
                upper_mass = mass
                break

        # Обробка випадків, коли target_mass за межами даних
        if not lower_mass:
            return aircraft_data[masses[0]]
        if not upper_mass:
            return aircraft_data[masses[-1]]

        # Коефіцієнт для лінійної інтерполяції
        lower_mass_int = int(lower_mass)
        upper_mass_int = int(upper_mass)
        ratio = (target_mass_int - lower_mass_int) / (upper_mass_int - lower_mass_int)

        # Інтерполяція даних для кожної температури
        interpolated = {}
        for temp in aircraft_data[lower_mass]:
            if temp not in aircraft_data[upper_mass]:
                continue

            # Збираємо спільні рівні польоту (FL)
            lower_points = {p["fl"]: p for p in aircraft_data[lower_mass][temp]}
            upper_points = {p["fl"]: p for p in aircraft_data[upper_mass][temp]}
            common_fls = sorted(
                set(lower_points.keys()) & set(upper_points.keys()),
                key=lambda x: int(x)
            )

            # Інтерполяція параметрів для кожного FL
            temp_data = []
            for fl in common_fls:
                lower = lower_points[fl]
                upper = upper_points[fl]

                temp_data.append({
                    "fl": fl,
                    "time": str(round(float(lower["time"]) + (
                                float(upper["time"]) - float(lower["time"])) * ratio, 2)),
                    "distance": str(round(float(lower["distance"]) + (
                                float(upper["distance"]) - float(lower["distance"])) * ratio, 2)),
                    "fuel": str(round(float(lower["fuel"]) + (
                                float(upper["fuel"]) - float(lower["fuel"])) * ratio, 2)),
                    "ias": lower["ias"],  # Беремо з нижчої маси (або можна інтерполювати)
                    "tas": str(round(
                        float(lower["tas"]) + (float(upper["tas"]) - float(lower["tas"])) * ratio,
                        2))
                })

            interpolated[temp] = temp_data

        return interpolated

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFuelCalculator(root)
    root.mainloop()