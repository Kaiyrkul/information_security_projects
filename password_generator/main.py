import argparse
import math
import secrets
import string

from flask import Flask, jsonify, request

app = Flask(__name__)

# Пороги для статуса (бит энтропии) — для API и CLI
_ENTROPY_WEAK = 60
_ENTROPY_MEDIUM = 80


def password_status(entropy):
    """Человекочитаемый статус надёжности по энтропии (для JSON и CLI)."""
    if entropy < _ENTROPY_WEAK:
        return "Weak"
    if entropy < _ENTROPY_MEDIUM:
        return "Medium"
    return "Secure"


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
    password = "".join(secrets.choice(chars) for _ in range(length))
    return password, charset_size


def _parse_no_flag(value):
    """True if the client asked to exclude this character class (no_* query param)."""
    if value is None:
        return False
    s = str(value).strip().lower()
    if s in ("0", "false", "no", "off"):
        return False
    return True


@app.route("/generate", methods=["GET"])
def generate():
    try:
        length = int(request.args.get("length", 16))
    except (TypeError, ValueError):
        return jsonify(error="length must be an integer"), 400
    if length < 1:
        return jsonify(error="length must be at least 1"), 400

    use_digits = not _parse_no_flag(request.args.get("no_digits"))
    use_symbols = not _parse_no_flag(request.args.get("no_symbols"))
    use_upper = not _parse_no_flag(request.args.get("no_upper"))

    pwd, charset_size = generate_password(
        length, use_digits, use_symbols, use_upper
    )
    entropy = calculate_entropy(pwd, charset_size)
    status = password_status(entropy)

    return jsonify(password=pwd, entropy=entropy, status=status)


def run_cli(args):
    pwd, size = generate_password(
        args.length, args.digits, args.symbols, args.upper
    )
    entropy = calculate_entropy(pwd, size)
    status = password_status(entropy)

    print("\n" + "=" * 40)
    print(f"Сгенерированный пароль: {pwd}")
    print(f"Длина: {len(pwd)} | Мощность алфавита: {size}")
    print(f"Энтропия: {entropy} бит | Статус: {status}")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Secure Password Generator — API (по умолчанию) или CLI (подкоманда generate)"
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser(
        "generate",
        aliases=["gen"],
        help="Сгенерировать пароль в терминале (без запуска веб-сервера)",
    )
    gen.add_argument("-l", "--length", type=int, default=16, help="Длина пароля")
    gen.add_argument(
        "--no-digits",
        action="store_false",
        dest="digits",
        default=True,
        help="Исключить цифры",
    )
    gen.add_argument(
        "--no-symbols",
        action="store_false",
        dest="symbols",
        default=True,
        help="Исключить спецсимволы",
    )
    gen.add_argument(
        "--no-upper",
        action="store_false",
        dest="upper",
        default=True,
        help="Исключить заглавные буквы",
    )

    args = parser.parse_args()

    if args.command in ("generate", "gen"):
        run_cli(args)
    else:
        app.run(host="0.0.0.0", port=5000)
