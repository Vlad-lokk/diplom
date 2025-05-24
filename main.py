import tkinter as tk
from tkinter import ttk
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
            text="Висота в одиницях",
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
        print(route)
        sigments = calculate_route_segments(str(route))
        print(sigments)


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFuelCalculator(root)
    root.mainloop()