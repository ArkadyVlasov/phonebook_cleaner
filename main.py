import csv
import re
from pprint import pprint

def normalize_fio(record):
    """
    Распределяет части ФИО по трём первым полям.
    record: список из 7 элементов (полей CSV)
    Возвращает кортеж (lastname, firstname, surname)
    """
    # Объединяем первые три поля через пробел, игнорируя пустые строки
    full_name = ' '.join(part.strip() for part in record[:3] if part.strip())
    parts = full_name.split()
    lastname = parts[0] if len(parts) > 0 else ''
    firstname = parts[1] if len(parts) > 1 else ''
    surname = parts[2] if len(parts) > 2 else ''
    return lastname, firstname, surname

def normalize_phone(phone):
    """
    Приводит телефон к единому формату:
    +7(999)999-99-99 или +7(999)999-99-99 доб.9999
    """
    if not phone:
        return ''
    # Ищем добавочный номер (доб. или ext.)
    ext_match = re.search(r'(доб\.?|ext\.?)\s*(\d+)', phone, re.IGNORECASE)
    ext = ext_match.group(2) if ext_match else ''
    # Извлекаем все цифры из номера
    digits = re.sub(r'\D', '', phone)
    # Если добавочный найден и его цифры в конце, отрезаем их
    if ext and digits.endswith(ext):
        digits = digits[:-len(ext)]
    # Форматируем основной номер
    if len(digits) == 10:
        formatted = f"+7({digits[:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:]}"
    elif len(digits) == 11 and digits[0] in ('7', '8'):
        formatted = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    else:
        formatted = phone  # если формат не распознан, оставляем как есть
    if ext:
        formatted += f" доб.{ext}"
    return formatted

def merge_records(existing, new):
    """
    Объединяет две записи: для каждого поля берёт непустое значение.
    Если в new поле не пустое, оно заменяет existing.
    """
    merged = []
    for i in range(7):
        merged.append(new[i] if new[i] else existing[i])
    return merged

def main():
    # 1. Читаем исходную адресную книгу
    with open("phonebook_raw.csv", encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    # Сохраняем заголовок (первая строка), если он есть
    header = contacts_list[0] if contacts_list else None
    data = contacts_list[1:] if header else contacts_list

    # 2. Обрабатываем каждую запись (кроме заголовка)
    for record in data:
        # Нормализуем ФИО
        lastname, firstname, surname = normalize_fio(record)
        record[0] = lastname
        record[1] = firstname
        record[2] = surname
        # Нормализуем телефон (индекс 5)
        record[5] = normalize_phone(record[5])

    # 3. Объединяем дубликаты по (lastname, firstname)
    unique = {}
    for record in data:
        key = (record[0], record[1])  # фамилия и имя
        if key in unique:
            unique[key] = merge_records(unique[key], record)
        else:
            unique[key] = record

    # 4. Формируем результат с заголовком
    result = [header] + list(unique.values()) if header else list(unique.values())

    # 5. Сохраняем результат
    with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(result)

    print("Готово! Результат сохранён в phonebook.csv")
    # Выведем первые 5 строк для проверки (по желанию)
    pprint(result[:5])

if __name__ == "__main__":
    main()