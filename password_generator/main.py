import argparse
import math
import secrets
import string
import sys

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Entropy thresholds (bits) for API and CLI status labels
_ENTROPY_WEAK = 60
_ENTROPY_MEDIUM = 80
# Prevent excessive length values (basic memory/CPU DoS guard)
_MAX_PASSWORD_LENGTH = 256


def password_status(entropy):
    """Human-readable password strength status for JSON and CLI."""
    if entropy < _ENTROPY_WEAK:
        return "Weak"
    if entropy < _ENTROPY_MEDIUM:
        return "Medium"
    return "Secure"


def calculate_entropy(password, charset_size):
    """Calculate password entropy: E = L * log2(R)."""
    if not password or charset_size < 1:
        return 0
    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)


def build_charset(use_lower, use_upper, use_digits, use_symbols):
    """Build charset from enabled symbol classes. Empty result means all classes are disabled."""
    parts = []
    size = 0
    if use_lower:
        parts.append(string.ascii_lowercase)
        size += 26
    if use_upper:
        parts.append(string.ascii_uppercase)
        size += 26
    if use_digits:
        parts.append(string.digits)
        size += 10
    if use_symbols:
        parts.append(string.punctuation)
        size += len(string.punctuation)
    return "".join(parts), size


def generate_password(length, use_lower, use_upper, use_digits, use_symbols):
    chars, charset_size = build_charset(
        use_lower, use_upper, use_digits, use_symbols
    )
    if charset_size == 0:
        raise ValueError("at least one character set must be enabled")
    # Use secrets for cryptographic randomness
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


@app.route("/")
def index():
    """Web UI entrypoint; JSON API stays on /generate."""
    return render_template("index.html", max_length=_MAX_PASSWORD_LENGTH)


@app.route("/generate", methods=["GET"])
def generate():
    try:
        length = int(request.args.get("length", 16))
    except (TypeError, ValueError):
        return jsonify(error="length must be an integer"), 400
    if length < 1:
        return jsonify(error="length must be at least 1"), 400
    if length > _MAX_PASSWORD_LENGTH:
        return (
            jsonify(
                error="length too large",
                max_length=_MAX_PASSWORD_LENGTH,
            ),
            400,
        )

    use_lower = not _parse_no_flag(request.args.get("no_lower"))
    use_digits = not _parse_no_flag(request.args.get("no_digits"))
    use_symbols = not _parse_no_flag(request.args.get("no_symbols"))
    use_upper = not _parse_no_flag(request.args.get("no_upper"))

    try:
        pwd, charset_size = generate_password(
            length, use_lower, use_upper, use_digits, use_symbols
        )
    except ValueError as e:
        return jsonify(error=str(e)), 400
    entropy = calculate_entropy(pwd, charset_size)
    status = password_status(entropy)

    return jsonify(password=pwd, entropy=entropy, status=status)


def run_cli(args):
    if args.length < 1:
        print("Error: length must be at least 1.", file=sys.stderr)
        sys.exit(1)
    if args.length > _MAX_PASSWORD_LENGTH:
        print(
            f"Error: length must be <= {_MAX_PASSWORD_LENGTH} (requested {args.length}).",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        pwd, size = generate_password(
            args.length,
            args.lower,
            args.upper,
            args.digits,
            args.symbols,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    entropy = calculate_entropy(pwd, size)
    status = password_status(entropy)

    print("\n" + "=" * 40)
    print(f"Generated password: {pwd}")
    print(f"Length: {len(pwd)} | Charset size: {size}")
    print(f"Entropy: {entropy} bits | Status: {status}")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Secure Password Generator — API by default or CLI via the generate subcommand"
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser(
        "generate",
        aliases=["gen"],
        help="Generate a password in terminal (without running web server)",
    )
    gen.add_argument("-l", "--length", type=int, default=16, help="Password length")
    gen.add_argument(
        "--no-lower",
        action="store_false",
        dest="lower",
        default=True,
        help="Exclude lowercase letters",
    )
    gen.add_argument(
        "--no-digits",
        action="store_false",
        dest="digits",
        default=True,
        help="Exclude digits",
    )
    gen.add_argument(
        "--no-symbols",
        action="store_false",
        dest="symbols",
        default=True,
        help="Exclude symbols",
    )
    gen.add_argument(
        "--no-upper",
        action="store_false",
        dest="upper",
        default=True,
        help="Exclude uppercase letters",
    )

    args = parser.parse_args()

    if args.command in ("generate", "gen"):
        run_cli(args)
    else:
        app.run(host="0.0.0.0", port=5000)
