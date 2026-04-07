# information_security_projects

## Secure Password Infrastructure

This repository contains an integrated security solution consisting of a high-entropy password generation service and a hardened Nginx reverse proxy for DDoS protection.

## Project Structure
- `/password_generator`: Flask-based microservice for secure password generation.
- `/nginx_proxy`: Infrastructure layer with Nginx configuration and Docker orchestration.

---

## Project 1: Secure Password Generator (Backend)
**Core Security Logic:**
- **CSPRNG:** Uses the `secrets` module for cryptographically strong randomness.
- **Entropy Analysis:** Implements Shannon entropy calculation: $E = L \cdot \log_2(R)$.
- **Status Classification:** Automatically labels passwords as `Weak` (<60 bits), `Medium`, or `Secure` (>80 bits).
- **Dual Interface:** Supports both **CLI** mode for local use and **REST API** for web integration.

## Project 2: Nginx DDoS Protection (Infrastructure)
**Security Hardening:**
- **Rate Limiting:** Restricted to 2 requests/sec per IP with a burst of 5 to prevent HTTP Flood attacks.
- **Surface Reduction:** `server_tokens off` to hide Nginx version from scanners.
- **Payload Security:** `client_max_body_size 1k` to prevent large buffer overflow attempts.
- **Security Headers:** Implemented `X-Frame-Options` and `X-Content-Type-Options`.

---

## Deployment & Demo
### 1. Run with Docker Compose
```bash
cd nginx_proxy
docker-compose up --build
