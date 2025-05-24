import json
import math
import tkinter as tk
from tkinter import ttk, filedialog
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AdvancedFuelCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Розрахунок палива Boeing 737-800")

        # Константи
        self.standard_mass_kg = 70500  # Середня операційна маса (MZFW)
        self.kg_to_lbs = 2.20462

        self.aircraft_data = None
        self.route_points = tk.StringVar()
        self.fuel_consumed_kg = 0.0

        self.create_widgets()
        self.setup_graph()
        self.load_aircraft_data()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Параметри польоту")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Маршрут (ідентифікатори через кому):").grid(row=0, column=0)
        ttk.Entry(input_frame, textvariable=self.route_points, width=40).grid(row=0, column=1)

        ttk.Button(input_frame, text="Розрахувати", command=self.calculate).grid(row=1, column=0,
                                                                                 columnspan=2,
                                                                                 pady=10)

        self.output_text = tk.Text(self.root, height=15, width=70)
        self.output_text.grid(row=1, column=0, padx=10, pady=10)

    def setup_graph(self):
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10)

    def load_aircraft_data(self):
        try:
            with open('../src/boeing-738-climb.json', 'r') as f:
                self.aircraft_data = json.load(f)
        except Exception as e:
            self.show_error(f"Помилка завантаження даних літака: {str(e)}")

    def calculate_route_segments(self, route_points):
        with open('../src/airports_esp.json', 'r', encoding='utf-8') as f:
            airports = {a['ident']: a for a in json.load(f)}

        with open('../src/vertices_esp.json', 'r', encoding='utf-8') as f:
            vertices = {v['ident']: v for v in json.load(f)}

        points = []
        for ident in route_points:
            point = airports.get(ident) or vertices.get(ident)
            if not point:
                raise ValueError(f"Точка {ident} не знайдена")
            points.append((
                point['latitude'],
                point['longitude'],
                point.get('altitude', 0)
            ))

        segments = []
        for i in range(len(points) - 1):
            start = (points[i][0], points[i][1])
            end = (points[i + 1][0], points[i + 1][1])
            distance_nm = geodesic(start, end).nautical
            alt_diff = abs(points[i + 1][2] - points[i][2])

            segments.append({
                'distance_nm': distance_nm,
                'altitude_ft': points[i + 1][2] * 3.28084  # Конвертація метрів у фути
            })

        return segments

    def get_fuel_flow(self, altitude_ft):
        mass_lbs = self.standard_mass_kg * self.kg_to_lbs
        closest_mass = min(self.aircraft_data.keys(), key=lambda x: abs(int(x) - mass_lbs))

        altitudes = sorted([int(fl) for fl in self.aircraft_data[closest_mass]])
        closest_fl = min(altitudes, key=lambda x: abs(x - altitude_ft // 100))

        return self.aircraft_data[closest_mass][str(closest_fl)]['fuel_kg_per_hour']

    def calculate(self):
        try:
            self.fuel_consumed_kg = 0
            route = "LEBL LOTOS TORDU DIKUT SOPET VLC SERRA ASTRO POBOS XEBAR YES MAMIS BAZAS VIBAS LEGA"
            route = route.split()
            if len(route) < 2:
                raise ValueError("Маршрут має містити мінімум дві точки")

            segments = self.calculate_route_segments(route)
            self.ax1.clear()
            self.ax2.clear()

            distances = []
            fuels = []
            altitudes = []

            for seg in segments:
                fuel_kg_h = self.get_fuel_flow(seg['altitude_ft'])
                time_h = seg['distance_nm'] / 450  # Припустима середня швидкість 450 KTAS
                fuel_kg = fuel_kg_h * time_h

                self.fuel_consumed_kg += fuel_kg
                distances.append(seg['distance_nm'])
                fuels.append(fuel_kg)
                altitudes.append(seg['altitude_ft'])

                self.output_text.insert(tk.END,
                                        f"Відрізок {seg['distance_nm']:.1f} NM | Висота {seg['altitude_ft']:.0f} ft\n"
                                        f"Витрата палива: {fuel_kg:.1f} кг | Час: {time_h * 60:.1f} хв\n\n"
                                        )

            # Оновлення графіків
            self.ax1.plot(np.cumsum(distances), fuels, 'b-')
            self.ax1.set_title('Витрата палива за маршрутом')
            self.ax1.set_xlabel('Дистанція (NM)')
            self.ax1.set_ylabel('Паливо (кг)')

            self.ax2.plot(np.cumsum(distances), altitudes, 'g-')
            self.ax2.set_title('Профіль висоти')
            self.ax2.set_xlabel('Дистанція (NM)')
            self.ax2.set_ylabel('Висота (ft)')

            self.canvas.draw()

            self.output_text.insert(tk.END,
                                    f"\nЗАГАЛЬНІ РЕЗУЛЬТАТИ:\n"
                                    f"Загальна витрата палива: {self.fuel_consumed_kg:.1f} кг\n"
                                    f"Загальна відстань: {sum(distances):.1f} NM\n"
                                    )

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, message):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"ПОМИЛКА: {message}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFuelCalculator(root)
    root.mainloop()