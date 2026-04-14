# information_security_projects

## Secure Password Infrastructure

This repository contains two connected parts:
1. a cryptographically secure password generator (`password_generator`);
2. an infrastructure security layer for incoming traffic (`nginx_proxy`).

The goal is to combine security at the **data level** (strong passwords) and at the **perimeter level** (request abuse resistance).

---

## Project Structure

- `password_generator` — Flask application with:
  - JSON API (`/generate`);
  - web interface (`/`);
  - CLI mode (`python main.py generate ...`).
- `nginx_proxy` — Nginx reverse proxy with rate limiting and basic hardening.

---

## How the Two Projects Work Together

`nginx_proxy` receives HTTP requests from users and forwards them to `password_generator`.

So:
- `password_generator` handles secure generation and password quality scoring;
- `nginx_proxy` protects the service from request spikes and reduces attack surface.

This is a classic **defense-in-depth** architecture.

---

## Project 1: Password Generator

### What It Does

- Generates passwords based on selected length and character sets;
- Calculates entropy using `E = L * log2(R)`;
- Returns a security status (`Weak`, `Medium`, `Secure`);
- Supports API, web UI, and CLI.

### Functions and Security Mechanisms Used (and Why)

#### 1) `secrets.choice(...)` (CSPRNG)
- Uses Python `secrets`, not `random`.
- **Why:** `random` is fine for simulations but is not suitable for security-sensitive randomness.
- `secrets` relies on OS-level secure randomness and is appropriate for password generation.

#### 2) Entropy calculation `L * log2(R)`
- `L` is password length, `R` is charset size.
- **Why:** this is a common, practical estimate of brute-force complexity for uniformly generated passwords.
- It gives users a measurable quality indicator.

#### 3) `build_charset(...)`
- Builds the final alphabet from enabled sets: lower/upper/digits/symbols.
- **Why:** keeps charset logic centralized, easier to validate and test edge cases.

#### 4) Input validation
- Length limits: minimum `1`, maximum `_MAX_PASSWORD_LENGTH` (`256`).
- Empty charset check (when all sets are disabled).
- **Why:** prevents invalid states and basic DoS attempts via oversized `length`.

#### 5) Safe error handling
- Invalid input returns `400` with JSON error details.
- **Why:** predictable API behavior is safer than uncaught exceptions (`500`).

#### 6) Web page on `/`
- HTML page calls `/generate` via `fetch` and displays results.
- **Why:** easier demonstration without `curl`, while API remains the integration interface.

---

## Project 2: Nginx Proxy (DDoS/Hardening Layer)

### What It Does

- Receives external requests;
- Limits request rate per client IP;
- Proxies traffic to the internal generator service;
- Reduces exposed server information.

### Directives Used (and Why)

#### 1) `limit_req_zone $binary_remote_addr zone=addr:10m rate=2r/s;`
- Tracks request counters by IP.
- **Why:** simple baseline protection from HTTP flood/abuse.

#### 2) `limit_req zone=addr burst=5;`
- Allows short bursts while limiting sustained overload.
- **Why:** balances user experience and abuse control.

#### 3) `server_tokens off;`
- Hides Nginx version details.
- **Why:** reduces useful fingerprinting data for automated scanners.

#### 4) `client_max_body_size 1k;`
- Restricts request body size.
- **Why:** cuts unnecessary attack surface for large payload attempts.

#### 5) Security headers
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- **Why:** baseline browser-side hardening against clickjacking and MIME sniffing.

---

## Information Security Logic Used in the Repository

1. **Cryptographic secret generation**
   - Password generation uses CSPRNG (`secrets`) only.
2. **Safe input handling**
   - Request parameters are validated;
   - Invalid cases return controlled errors.
3. **Abuse resistance**
   - Backend length limits;
   - Proxy-level rate limiting.
4. **Information minimization**
   - Server version tokens are hidden.
5. **Separation of responsibilities**
   - App layer = business logic;
   - Proxy layer = perimeter protection.

Why this design instead of putting everything in one place:
- easier maintenance and scaling;
- safer separation of concerns;
- more effective defense in depth.

---

## Run and Test (Detailed)

There are two ways to run the project: local Flask only, or Nginx + Docker.

### Option A: Run Password Generator Only (No Docker)

#### 1) Go to project directory
```powershell
cd D:\information_security_projects\password_generator
```

#### 2) Install dependencies
```powershell
pip install -r requirements.txt
```
If you do not use `requirements.txt`, this is enough:
```powershell
pip install flask
```

#### 3) Start Flask server
```powershell
python main.py
```

#### 4) Open in browser
- Web interface: `http://127.0.0.1:5000/`
- API endpoint: `http://127.0.0.1:5000/generate?length=16`

#### 5) Stop server
- Press `Ctrl + C` in the same terminal.

---

### Option B: Run Through Nginx + Docker Compose

> Requires Docker Desktop installed and available in terminal (`docker` command must work).

#### 1) Go to proxy directory
```powershell
cd D:\information_security_projects\nginx_proxy
```

#### 2) Start containers
```powershell
docker compose up --build
```

#### 3) Verify in browser
- Web interface through proxy: `http://127.0.0.1/`
- API through proxy: `http://127.0.0.1/generate?length=16`

#### 4) Stop containers
- Press `Ctrl + C` in the compose terminal.
- Optionally remove containers/network:
```powershell
docker compose down
```

---

## API Usage

### GET `/generate`

Query parameters:
- `length` — password length (`1..256`);
- `no_lower` — disable lowercase (`1/true/on`);
- `no_upper` — disable uppercase;
- `no_digits` — disable digits;
- `no_symbols` — disable symbols.

Example:
```text
/generate?length=20&no_symbols=1
```

Success response (`200`):
```json
{
  "password": "....",
  "entropy": 114.6,
  "status": "Secure"
}
```

Error responses (`400`):
- invalid `length`;
- length less than 1;
- length greater than `max_length`;
- all character sets disabled.

---

## CLI Usage

### Generate password in terminal
```powershell
cd D:\information_security_projects\password_generator
python main.py generate --length 24
```

Flag examples:
```powershell
python main.py generate --length 20 --no-symbols
python main.py generate --length 16 --no-lower --no-upper --no-symbols
```

CLI output includes:
- generated password;
- length and charset size;
- entropy in bits;
- security status.

---

## Limitations and Next Improvements

- Built-in Flask server is suitable for development, not production.
- For production: use WSGI (gunicorn/uwsgi), TLS/HTTPS, stronger security headers, and monitoring.
- Current version is focused on learning/demo goals with baseline information security practices.