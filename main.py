import json
import tkinter as tk
from tkinter import ttk, messagebox
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
            "LA CORUNA - BARCELONA": "LECO ROXER MASIP VES AMAKA LASKU RONSI OBETO SNR CALCE BLV GRAUS LEBL",
            "Свій": ""
        }

        self.create_widgets()
        self.setup_bindings()
        self.open_files()


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
            self.bg_image = Image.open('src/background2.png')
            self.bg_image = self.bg_image.resize((800, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas = tk.Canvas(self.master, width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except Exception as e:
            print(f"Помилка завантаження фону: {e}")
            self.canvas = tk.Canvas(self.master, width=800, height=600, bg='')
            self.canvas.pack()
        custom_font = ("Arial", 10, "bold")
        # Основний фрейм для віджетів
        self.widget_frame = tk.Frame(self.canvas, bd=5, relief='ridge', bg='')
        self.widget_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

        # Елементи інтерфейсу
        self.route_type_label = tk.Label(
            self.widget_frame,
            font=custom_font,
            bg='white',
            text="Рейс:"
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
            font=custom_font,
            text="Ваш маршрут:",
            bg='white'
        )
        self.custom_route_label.pack(pady=5)

        self.custom_route_entry = tk.Entry(
            self.widget_frame,
            width=45,
            state="disabled"
        )
        self.custom_route_entry.pack(pady=5)

        self.top_row_frame = tk.Frame(self.widget_frame, bg='')
        self.top_row_frame.pack(pady=5)
        self.bottom_row_frame = tk.Frame(self.widget_frame, bg='')
        self.bottom_row_frame.pack(pady=5)

        # Інші елементи...
        self.mass_label = tk.Label(
            self.top_row_frame,
            font=custom_font,
            text="Вага літака в КГ",
            bg='white'
        )
        self.mass_label.pack(side='left', padx=30)

        self.isa_label = tk.Label(
            self.top_row_frame,
            font=custom_font,
            text="ISA Deviation",
            bg='white'
        )

        self.mass_entry = tk.Entry(self.bottom_row_frame, width=10)
        self.mass_entry.pack(padx=55, side='left')
        self.mass_entry.insert(0, '65000')

        self.isa_label.pack(padx=30)
        self.isa_select = ttk.Combobox(
            self.bottom_row_frame,
            width=10,
            values=[-30,-25,-20,-15,-10,-5,0,5,10,15,25,30]
        )
        self.isa_select.pack(padx=40, side='left')
        self.isa_select.set(0)

        self.calculate_button = tk.Button(
            self.widget_frame,
            text="Розрахувати",
            font=custom_font,
            command=self._calculate_best_cost
        )
        self.calculate_button.pack(pady=5)

        self.progress = ttk.Progressbar(self.widget_frame, orient="horizontal", length=300, mode="determinate")

        self.tree = ttk.Treeview(self.widget_frame, columns=("Вхідні дані", "Результати"), show="headings")
        self.tree.heading("Вхідні дані", text="Вхідні дані")
        self.tree.heading("Результати", text="Результати")

        self.on_route_type_change()

    def _calculate_best_cost(self):
        try:
            self.calculate_best_cost()
        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка: {str(e)}")

    def open_files(self):
        with open('src/boeing-738-climb.json', 'r') as f:
            self.boeing_data_climb = json.load(f)

        with open('src/boeing-738-cruise.json', 'r') as f:
            self.boeing_data_cruise = json.load(f)

        with open('src/boeing-738-descent-modified.json', 'r') as f:
            self.boeing_data_descent = json.load(f)

    def validate_inputs(self):
        # Валідація маршруту
        route = self.custom_route_entry.get().strip()
        if not route:
            messagebox.showerror("Помилка", "Маршрут не може бути порожнім")
            return False

        mass = self.mass_entry.get().strip().upper()

        # Спроба витягнути числове значення (ігноруємо "FL" якщо введено)
        try:
            fl_value = int(mass.replace("FL", ""))
        except ValueError:
            messagebox.showerror("Помилка", "Невірний формат ваги\nПриклад: 40000")
            return False

        # Діапазон FL (можна змінити за потребою)
        if not (40000 <= fl_value <= 85000):
            messagebox.showerror("Помилка", "Маса повинна бути між 40000 та 85000")
            return False

        return True

    def set_progress(self, value):
        """
        Оновлює значення прогрес бара
        :param value: значення від 0 до 100
        """
        value = max(0, min(100, value))
        self.progress["value"] = value
        self.widget_frame.update_idletasks()

    def show_results(self, altitude_fl_start, altitude_fl_end, mass, distance_km, better_height, lowest_fuel_kg, total_time):
        # Приклад даних для виведення
        data = [
            [f"Початкова висота: {round(altitude_fl_start, 1)}FL", f"Оптимальна висота польоту: {round(better_height, 1)}FL"],
            [f"Кінцева висота: {round(altitude_fl_end, 1)}FL", f"Дистанція: {round(distance_km, 1)}км"],
            [f"Початкова маса літака: {mass}кг", f"Використано палива: {round(lowest_fuel_kg, 1)}кг"],
            [f"", f"Кінцева маса літака: {round(self.mass_kg, 1)}кг"],
            [f"", f"Час рейсу: {round(total_time, 1)}хв"],
        ]

        # Очистити таблицю (якщо вже були дані)
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Додати нові дані
        for row in data:
            self.tree.insert("", "end", values=row)

    def calculate_best_cost(self):
        self.tree.pack_forget()
        self.tree.place(x=1000, y=0)
        if not self.validate_inputs():
            return

        route = self.custom_route_entry.get()
        mass = int(self.mass_entry.get())

        distance_km, altitude_fl_start, altitude_fl_end = calculate_route_segments(route)

        fl_test = max(altitude_fl_start, altitude_fl_end)

        lowest_fuel_kg = 0
        better_height = 0
        total_time = 0
        self.progress.pack()
        self.widget_frame.update_idletasks()
        try:
            for i in range(int(fl_test), 410):
                self.set_progress(i/4)
                self.mass_kg = mass
                result = self.calculate_cost(route, i, distance_km, altitude_fl_start, altitude_fl_end)
                if lowest_fuel_kg and result[2] < lowest_fuel_kg:
                    lowest_fuel_kg = result[2]
                    better_height = i
                    total_time = result[0]
                else:
                    lowest_fuel_kg = result[2]
        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка: {str(e)}")
        finally:
            self.tree.pack(padx=20, expand=True)
            self.widget_frame.update_idletasks()
            self.show_results(altitude_fl_start, altitude_fl_end, mass, distance_km, better_height, lowest_fuel_kg, total_time)

        print(lowest_fuel_kg, better_height)


    def calculate_cost(self, route, height_fl, distance_km, altitude_fl_start, altitude_fl_end):

        print(height_fl, distance_km, self.mass_kg)

        climb_info = self.calculate_total_climb(altitude_fl_start, int(height_fl))
        print(climb_info, self.mass_kg)
        first_descent_info = self.calculate_total_descent(int(height_fl), altitude_fl_end,
                                                          calculate_mass=False)

        cruise_distance = distance_km - climb_info['total_distance'] - first_descent_info[
            'total_distance']

        cruise_info = self.calculate_cruise(cruise_distance, int(height_fl))

        print(cruise_info, self.mass_kg)

        descent_info = self.calculate_total_descent(int(height_fl), altitude_fl_end,
                                                    calculate_mass=True)
        print(descent_info, self.mass_kg)



        total_info = (climb_info['total_time'] + cruise_info['total_time'] + descent_info['total_time'],
              climb_info['total_distance'] + cruise_info['total_distance'] + descent_info[
                  'total_distance'],
              climb_info['total_fuel'] + cruise_info['total_fuel'] + descent_info['total_fuel'])
        print(total_info)
        return total_info

    def calculate_cruise(self, distance_km, flight_level):
        distance_nm = distance_km / 1.852  # Конвертація в морські милі
        total_fuel = 0.0
        total_time = 0.0
        remaining_distance = distance_nm
        current_mass = self.mass_kg  # Початкова маса

        while remaining_distance > 0:
            segment = min(5.0, remaining_distance)  # Сегмент 5 NM або менше

            # 1. Інтерполяція даних для поточної маси
            interpolated_data = self.interpolate_mass(self.boeing_data_cruise)

            fl_data = self.interpolate_isa(interpolated_data, self.isa_select.get())

            # 2. Знаходимо найближчі FL для інтерполяції
            fl_values = sorted([int(item['fl']) for item in fl_data], key=lambda x: x)
            lower_fl, upper_fl = None, None

            # Пошук найближчих FL
            for i, fl in enumerate(fl_values):
                if fl >= flight_level:
                    upper_fl = fl
                    lower_fl = fl_values[i - 1] if i > 0 else fl
                    break
            else:
                lower_fl = upper_fl = fl_values[-1]

            # 3. Інтерполяція TAS та витрати палива
            lower_entry = next(item for item in fl_data if int(item['fl']) == lower_fl)
            upper_entry = next(item for item in fl_data if int(item['fl']) == upper_fl)

            # Лінійна інтерполяція
            if lower_fl == upper_fl:
                tas = float(lower_entry['tas'])
                fuel_flow = float(lower_entry['fuel'])
            else:
                ratio = (flight_level - lower_fl) / (upper_fl - lower_fl)
                tas = float(lower_entry['tas']) + (
                            float(upper_entry['tas']) - float(lower_entry['tas'])) * ratio
                fuel_flow = float(lower_entry['fuel']) + (
                            float(upper_entry['fuel']) - float(lower_entry['fuel'])) * ratio

            # 4. Розрахунок часу та палива для сегмента
            time_segment = segment / tas  # Час у годинах
            fuel_segment = fuel_flow * time_segment

            # 5. Оновлення даних
            total_time += time_segment
            total_fuel += fuel_segment
            self.mass_kg -= fuel_segment  # Зменшення маси
            remaining_distance -= segment

        return {
            'total_time': round(total_time * 60, 2),
            'total_distance': round(distance_km, 2),
            'total_fuel': round(total_fuel, 2)
        }



    def calculate_descent(self, fl_target):
        # Використовуємо дані для спуску


        descent_data = self.interpolate_mass(self.boeing_data_descent)

        descent_data = self.interpolate_isa(descent_data, self.isa_select.get())

        # Сортуємо точки за зворотнім порядком FL (від більших до менших)
        sorted_data = sorted(descent_data, key=lambda x: int(x['fl']))
        fls = [int(point['fl']) for point in sorted_data]

        # Обробка випадків за межами даних
        if fl_target >= fls[0]:  # Найвищий доступний FL у даних спуску
            return {
                'time': float(sorted_data[0]['time']),
                'distance': float(sorted_data[0]['distance']),
                'fuel': float(sorted_data[0]['fuel'])
            }
        elif fl_target <= fls[-1]:  # Найнижчий доступний FL
            return {
                'time': float(sorted_data[-1]['time']),
                'distance': float(sorted_data[-1]['distance']),
                'fuel': float(sorted_data[-1]['fuel'])
            }

        # Знаходимо інтервал для інтерполяції
        for i in range(1, len(fls)):
            if fls[i] <= fl_target:
                upper_idx = i - 1  # Вищий FL
                lower_idx = i  # Нижчий FL
                break

        # Лінійна інтерполяція
        fl_high = fls[upper_idx]
        fl_low = fls[lower_idx]
        ratio = (fl_high - fl_target) / (fl_high - fl_low)

        upper_point = sorted_data[upper_idx]
        lower_point = sorted_data[lower_idx]

        return {
            'time': round(float(upper_point['time']) +
                          (float(lower_point['time']) - float(upper_point['time'])) * ratio, 2),
            'distance': round(float(upper_point['distance']) +
                              (float(lower_point['distance']) - float(
                                  upper_point['distance'])) * ratio, 2),
            'fuel': round(float(upper_point['fuel']) +
                          (float(lower_point['fuel']) - float(upper_point['fuel'])) * ratio, 2)
        }

    def calculate_total_descent(self, fl_start, fl_end, calculate_mass):
        # Для спуску fl_start має бути вищим за fl_end
        if fl_start < fl_end:
            fl_start, fl_end = fl_end, fl_start

        # Інтерполяція для меж
        start_data = self.calculate_descent(fl_start)
        end_data = self.calculate_descent(fl_end)

        # Знаходимо всі FL з файлу в діапазоні [fl_start, fl_end]
        descent_data = self.interpolate_mass(self.boeing_data_descent)

        descent_data = self.interpolate_isa(descent_data, self.isa_select.get())

        sorted_fls = sorted([int(p['fl']) for p in descent_data], reverse=True)
        relevant_fls = [fl for fl in sorted_fls if fl_end <= fl <= fl_start]

        total_time = start_data['time'] - end_data['time']
        total_distance = start_data['distance'] - end_data['distance']
        total_fuel = start_data['fuel'] - end_data['fuel']

        # Коригування для проміжних точок
        if relevant_fls:
            first_fl = relevant_fls[0]
            last_fl = relevant_fls[-1]

            # Віднімаємо значення між кінцевими точками даних
            first_data = next(p for p in descent_data if int(p['fl']) == first_fl)
            last_data = next(p for p in descent_data if int(p['fl']) == last_fl)
            total_time -= (float(first_data['time']) - float(last_data['time']))
            total_distance -= (float(first_data['distance']) - float(last_data['distance']))
            total_fuel -= (float(first_data['fuel']) - float(last_data['fuel']))
            if calculate_mass:
                self.mass_kg = self.mass_kg - (float(first_data['fuel']) - float(last_data['fuel']))

        return {
            'total_time': abs(round(total_time, 2)),
            'total_distance': abs(round(total_distance, 2)),
            'total_fuel': abs(round(total_fuel, 2))
        }

    def calculate_climb(self, fl_target):
        # Сортуємо точки за значенням FL

        climb_data = self.interpolate_mass(self.boeing_data_climb)

        climb_data = self.interpolate_isa(climb_data, self.isa_select.get())

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

        climb_data = self.interpolate_mass(self.boeing_data_climb)

        climb_data = self.interpolate_isa(climb_data, self.isa_select.get())

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
            current_data = self.calculate_climb(current_fl)
            next_data = self.calculate_climb(next_fl)

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

    def interpolate_mass(self, aircraft_data):

        target_mass = self.mass_kg

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
                                float(upper["time"]) - float(lower["time"])) * ratio, 2)) if "time" in lower and "time" in upper else 0,
                    "distance": str(round(float(lower["distance"]) + (
                                float(upper["distance"]) - float(lower["distance"])) * ratio, 2)) if "distance" in upper and "distance" in lower else 0,
                    "fuel": str(round(float(lower["fuel"]) + (
                                float(upper["fuel"]) - float(lower["fuel"])) * ratio, 2)),
                    "ias": lower["ias"] if "ias" in lower else 0,
                    "tas": str(round(
                        float(lower["tas"]) + (float(upper["tas"]) - float(lower["tas"])) * ratio,
                        2))
                })

            interpolated[temp] = temp_data

        return interpolated

    def interpolate_isa(self, data, target_isa):
        """
        Лінійна інтерполяція даних за значенням ISA.
        :param data: Словник з даними, де ключі верхнього рівня — значення ISA (наприклад, '0', '10').
        :param target_isa: Цільове значення ISA для інтерполяції.
        :return: Інтерпольовані дані для заданого ISA.
        """
        # Конвертуємо ключі ISA в int для коректного сортування
        isa_keys = sorted(data.keys(), key=lambda x: int(x))
        target_isa_int = int(target_isa)

        # Якщо значення ISA вже є в даних, повертаємо його
        if str(target_isa) in isa_keys:
            return data[str(target_isa)]

        # Знаходимо найближчі значення ISA
        lower_isa, upper_isa = None, None
        for isa in isa_keys:
            isa_int = int(isa)
            if isa_int <= target_isa_int:
                lower_isa = isa
            elif isa_int > target_isa_int and upper_isa is None:
                upper_isa = isa
                break

        # Обробка крайніх випадків
        if not lower_isa:
            return data[isa_keys[0]]
        if not upper_isa:
            return data[isa_keys[-1]]

        # Коефіцієнт інтерполяції
        lower_isa_int = int(lower_isa)
        upper_isa_int = int(upper_isa)
        ratio = (target_isa_int - lower_isa_int) / (upper_isa_int - lower_isa_int)

        # Інтерполяція параметрів для кожного FL
        interpolated = []
        lower_data = data[lower_isa]
        upper_data = data[upper_isa]

        # Збираємо спільні FL
        lower_fls = {entry['fl']: entry for entry in lower_data}
        upper_fls = {entry['fl']: entry for entry in upper_data}
        common_fls = sorted(
            set(lower_fls.keys()) & set(upper_fls.keys()),
            key=lambda x: int(x)
        )

        for fl in common_fls:
            lower_entry = lower_fls[fl]
            upper_entry = upper_fls[fl]
            interpolated_entry = {'fl': fl}

            # Інтерполяція кожного параметра
            for key in lower_entry:
                if key == 'fl':
                    continue
                if key in upper_entry:
                    try:
                        lower_val = float(lower_entry[key])
                        upper_val = float(upper_entry[key])
                        interpolated_val = lower_val + (upper_val - lower_val) * ratio
                        interpolated_entry[key] = round(interpolated_val, 2)
                    except (ValueError, TypeError):
                        interpolated_entry[key] = lower_entry[key]
                else:
                    interpolated_entry[key] = lower_entry.get(key, 0)

            interpolated.append(interpolated_entry)

        return interpolated

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFuelCalculator(root)
    root.mainloop()