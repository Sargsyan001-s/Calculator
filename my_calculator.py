import math
import threading
import json
import os
import time
import datetime

# 1. Класс калькулятора
class Calculator:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def subtract(a, b):
        return a - b

    @staticmethod
    def multiply(a, b):
        return a * b

    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Невозможно разделить на ноль")
        return a / b

    @staticmethod
    def power(a, b):
        return a ** b

    @staticmethod
    def sqrt(a):
        if a < 0:
            raise ValueError("Не удается вычислить квадратный корень из отрицательного числа")
        return math.sqrt(a)

# 2. Функции для работы с файлами (многопоточность)
def save_to_file(filename, data):
    with open(filename, 'a') as file:
        file.write(data + '\n')

def threaded_save(filename, data):
    thread = threading.Thread(target=save_to_file, args=(filename, data))
    thread.start()

# 3. Функции для авторизации и регистрации
USER_DATA_FILE = 'users.json'

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

def register(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username in users and users[username] == password:
        return True
    return False

# 4. Логирование действий и ошибок
def log_action(username, action, error=False):
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    log_type = "ERROR" if error else "INFO"
    log_entry = f"[{log_type}] [{timestamp}] [{username}] – {action}"
    threaded_save('app.log', log_entry)

# 5. Фоновый поток для проверки лицензии
LICENSE_FILE = 'license.json'

def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_license(license_data):
    with open(LICENSE_FILE, 'w') as file:
        json.dump(license_data, file)

class LicenseChecker(threading.Thread):
    def __init__(self, license_duration):
        super().__init__()
        self.license_duration = license_duration
        self.license_data = load_license()
        self.running = True

    def is_license_valid(self):
        if "start_time" not in self.license_data or "key" not in self.license_data:
            return False
        elapsed_time = time.time() - self.license_data["start_time"]
        return elapsed_time <= self.license_duration

    def run(self):
        while self.running:
            if not self.is_license_valid():
                print("Лицензия истекла! Пожалуйста, введите новый лицензионный ключ.")
                self.running = False
            time.sleep(1)

    def stop(self):
        self.running = False

def main():
    license_checker = LicenseChecker(200)  # 200 секунд для теста
    license_data = load_license()

    # Если лицензия отсутствует или недействительна, запросить новый ключ
    if "start_time" not in license_data or "key" not in license_data or not license_checker.is_license_valid():
        license_key = input("Введите лицензионный ключ: ")
        license_data = {"key": license_key, "start_time": time.time()}
        save_license(license_data)
        print("Лицензия активирована!")
    else:
        print("Лицензия действительна. Программа запущена.")

    # Запуск проверки лицензии в фоновом режиме
    license_checker.start()

    while license_checker.running:
        print("1. Регистрация")
        print("2. Вход")
        choice = input("Выберите действие: ")

        if choice == '1':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            if register(username, password):
                print("Регистрация успешна!")
            else:
                print("Пользователь уже существует!")

        elif choice == '2':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            if login(username, password):
                print("Вход выполнен успешно!")
                log_action(username, "вошел в систему")
                while True:
                    print("1. Сложение")
                    print("2. Вычитание")
                    print("3. Умножение")
                    print("4. Деление")
                    print("5. Возведение в степень")
                    print("6. Квадратный корень")
                    print("7. Выход")
                    operation = input("Выберите операцию: ")

                    if operation == '7':
                        log_action(username, "вышел из системы")
                        break

                    try:
                        a = float(input("Введите первое число: "))
                        if operation != '6':
                            b = float(input("Введите второе число: "))

                        if operation == '1':
                            result = Calculator.add(a, b)
                        elif operation == '2':
                            result = Calculator.subtract(a, b)
                        elif operation == '3':
                            result = Calculator.multiply(a, b)
                        elif operation == '4':
                            result = Calculator.divide(a, b)
                        elif operation == '5':
                            result = Calculator.power(a, b)
                        elif operation == '6':
                            result = Calculator.sqrt(a)

                        print(f"Результат: {result}")
                        log_action(username, f"выполнил операцию {operation} с результатом {result}")

                    except ValueError as e:
                        print(f"Ошибка: {e}")
                        log_action(username, f"ошибка при выполнении операции: {e}", error=True)

            else:
                print("Неверное имя пользователя или пароль!")

    # Остановка фонового потока и завершение программы
    license_checker.stop()
    license_checker.join()
    print("Программа завершена из-за истечения лицензии.")
    exit(0)  # Завершение программы

if __name__ == "__main__":
    main()