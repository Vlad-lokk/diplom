import json

# Завантаження даних з файлу
with open('boeing-738-descent.json', 'r') as file:
    data = json.load(file)

# Ітерація через всі рівні структури даних
for top_key in data:
    for wind_key in data[top_key]:
        for entry in data[top_key][wind_key]:
            fl_value = entry['fl']
            # Видалення двох останніх символів (нулів)
            if len(fl_value) >= 2:
                entry['fl'] = fl_value[:-2]
            else:
                entry['fl'] = fl_value  # на випадок некоректних даних

# Збереження оновлених даних у новий файл
with open('boeing-738-descent-modified.json', 'w') as file:
    json.dump(data, file, indent=4)