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
    #Сохраняет данные пользователей в файл
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

def register(username, password):
    # Регистрирует нового пользователя
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login(username, password):
    #Авторизует пользователя
    users = load_users()
    if username in users and users[username] == password:
        return True
    return False

# 4. Логирование действий и ошибок
def log_action(username, action, error=False):
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") # Текущее время
    log_type = "ERROR" if error else "INFO" # Тип записи (ошибка или информация)
    log_entry = f"[{log_type}] [{timestamp}] [{username}] – {action}" # Формат записи
    threaded_save('app.log', log_entry)  # Сохраняем запись в файл в отдельном потоке

# 5. Фоновый поток для проверки лицензии
class LicenseChecker(threading.Thread):
    def __init__(self, license_duration):
        #Инициализация потока
        super().__init__()
        self.license_duration = license_duration
        self.start_time = time.time()# Время начала работы программы
        self.running = True 

    def run(self):
        while self.running:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > self.license_duration:
                print("Пробная лицензия программы завершена, чтобы продолжить работу приобретите лицензионный ключ!")
                self.running = False
            time.sleep(1)

    def stop(self):
        self.running = False


def main():
    # Запуск фонового потока для проверки лицензии
    license_checker = LicenseChecker(1800)  
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
                log_action(username, "вошел в систему")  # Логирование входа
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
                        log_action(username, "вышел из системы")  # Логирование выхода
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
                        log_action(username, f"выполнил операцию {operation} с результатом {result}")  # Логирование операции

                    except ValueError as e:
                        print(f"Ошибка: {e}")
                        log_action(username, f"ошибка при выполнении операции: {e}", error=True)  # Логирование ошибки

            else:
                print("Неверное имя пользователя или пароль!")

     # Остановка фонового потока при завершении программы
    license_checker.stop()
    license_checker.join()

if __name__ == "__main__":
    main()