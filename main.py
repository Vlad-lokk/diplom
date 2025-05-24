import tkinter as tk
from tkinter import ttk


class AdvancedFuelCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Розширений калькулятор пального")
        master.geometry("800x600")
        master.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Combobox для вибору типу пального
        self.fuel_type_label = tk.Label(self.master, text="Тип пального:")
        self.fuel_type_label.pack(pady=5)

        self.fuel_type = ttk.Combobox(
            self.master,
            values=["АІ-95", "АІ-98", "Дизель", "Газ"]
        )
        self.fuel_type.pack(pady=5)
        self.fuel_type.set("АІ-95")

        # Поле вводу для кількості літрів
        self.liters_label = tk.Label(self.master, text="Кількість літрів:")
        self.liters_label.pack(pady=5)

        self.liters_entry = tk.Entry(self.master, width=20)
        self.liters_entry.pack(pady=5)

        # Поле вводу для ціни за літр
        self.price_label = tk.Label(self.master, text="Ціна за літр (грн):")
        self.price_label.pack(pady=5)

        self.price_entry = tk.Entry(self.master, width=20)
        self.price_entry.pack(pady=5)

        # Кнопка розрахунку
        self.calculate_button = tk.Button(
            self.master,
            text="Розрахувати вартість",
            command=self.calculate_cost
        )
        self.calculate_button.pack(pady=20)

        # Поле для виводу результату
        self.result_label = tk.Label(self.master, text="Результат:", font=('Arial', 12))
        self.result_label.pack(pady=10)

        self.result_var = tk.StringVar()
        self.result_display = tk.Label(
            self.master,
            textvariable=self.result_var,
            font=('Arial', 14, 'bold'),
            fg='blue'
        )
        self.result_display.pack(pady=10)

    def calculate_cost(self):
        try:
            liters = float(self.liters_entry.get())
            price = float(self.price_entry.get())
            total = liters * price
            fuel_type = self.fuel_type.get()

            self.result_var.set(
                f"Вартість {liters}л {fuel_type} по {price}грн/л: {total:.2f}грн"
            )
        except ValueError:
            self.result_var.set("Будь ласка, введіть коректні числові значення!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFuelCalculator(root)
    root.mainloop()