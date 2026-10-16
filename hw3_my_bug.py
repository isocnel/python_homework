# Багованный код
grades = dict.fromkeys(["Python", "SQL"], [])

grades["Python"].append(5)

print("Оценки по Python:", grades["Python"])
print("Оценки по SQL:", grades["SQL"])

# 2. Объяснение бага
# При создании словаря оба ключа получают ссылку на один и тот же список.
# Поэтому добавление оценки по Python также изменяет список оценок по SQL.

# 3. Исправленная версия
grades = {}
grades["Python"] = []
grades["SQL"] = []

grades["Python"].append(5)

print("Оценки по Python:", grades["Python"])
print("Оценки по SQL:", grades["SQL"])
