# Secure Password Generator (CLI Tool)

## 1. Project Overview
This is a cryptographically secure command-line interface (CLI) tool designed to generate high-entropy passwords. The project focuses on the core principles of information security: randomness, complexity, and resistance to brute-force attacks.

### The Problem it Solves
Standard random number generators (like Python's `random` module) are PRNGs (Pseudo-Random Number Generators) and are predictable if the seed is known. This tool addresses that vulnerability by using system-level entropy for true cryptographic security.

## 2. Technical Architecture
The tool is built using **Python 3** and leverages the following security-focused components:

* **CSPRNG (Secrets Module):** Uses `secrets.choice()`, which relies on the most secure source of randomness provided by the operating system (e.g., `/dev/urandom` on Linux/macOS or `CryptGenRandom` on Windows).
* **Entropy Estimation:** Implements a mathematical model to calculate the information theoretical strength of the generated password.
* **Modular Alphabet:** Dynamically constructs the character set based on user-defined complexity constraints.

## 3. Security Metrics: Entropy Calculation
The strength of each password is measured in **Bits of Entropy** using the formula:
$$E = L \cdot \log_2(R)$$
Where:
* **L** = Length of the password.
* **R** = Size of the pool of unique characters (Alphabet).

**Strength Thresholds:**
* **< 60 bits:** Weak (Vulnerable to modern GPU cracking).
* **60 - 80 bits:** Medium (Safe for most personal accounts).
* **> 80 bits:** Strong (High resistance to distributed brute-force attacks).

## 4. Tech Stack
* **Language:** Python 3.10+
* **Libraries:** * `secrets`: For cryptographic randomness.
    * `argparse`: For professional CLI argument parsing.
    * `string`: For robust character set management.
    * `math`: For logarithmic entropy calculations.

## 5. Setup & Usage Instructions

### Prerequisites
- Python 3.x installed on your machine.
