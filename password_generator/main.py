import argparse
import secrets
import string
import math

def calculate_entropy(password, charset_size):
    """Считает энтропию пароля: E = L * log2(R)"""
    if not password:
        return 0
    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)

def generate_password(length, use_digits, use_symbols, use_upper):
    # Набор символов: всегда начинаем со строчных букв
    chars = string.ascii_lowercase
    charset_size = 26
    
    if use_upper:
        chars += string.ascii_uppercase
        charset_size += 26
    if use_digits:
        chars += string.digits
        charset_size += 10
    if use_symbols:
        chars += string.punctuation
        charset_size += len(string.punctuation)

    # Используем secrets для криптографической безопасности
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password, charset_size

def main():
    parser = argparse.ArgumentParser(description="Secure Password Generator for AUCA InfoSec")
    parser.add_argument("-l", "--length", type=int, default=16, help="Длина пароля")
    parser.add_argument("--no-digits", action="store_false", dest="digits", help="Исключить цифры")
    parser.add_argument("--no-symbols", action="store_false", dest="symbols", help="Исключить спецсимволы")
    parser.add_argument("--no-upper", action="store_false", dest="upper", help="Исключить заглавные буквы")

    args = parser.parse_args()

    # Генерация
    pwd, size = generate_password(args.length, args.digits, args.symbols, args.upper)
    # Расчет энтропии (теоретическая база для ИБ)
    entropy = calculate_entropy(pwd, size)

    print("\n" + "="*40)
    print(f"Сгенерированный пароль: \033[92m{pwd}\033[0m")
    print(f"Длина: {len(pwd)} | Мощность алфавита: {size}")
    print(f"Энтропия: {entropy} бит")
    
    # Вердикт по надежности
    if entropy < 60:
        print("Статус: \033[91mСЛАБЫЙ\033[0m")
    elif entropy < 80:
        print("Статус: \033[93mСРЕДНИЙ\033[0m")
    else:
        print("Статус: \033[94mНАДЕЖНЫЙ\033[0m")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()