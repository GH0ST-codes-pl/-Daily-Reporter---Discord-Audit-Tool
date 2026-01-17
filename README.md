# Daily Reporter - Discord Audit Tool

![Daily Reporter Banner](https://img.shields.io/badge/Daily-Reporter-red?style=for-the-badge&logo=discord)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux-green?style=for-the-badge)

**Daily Reporter** is an advanced, lightweight Discord reporting tool designed for educational and testing purposes. It features a sleek, colorful CLI, automatic ID extraction from URLs, and multi-threaded reporting capabilities.

**Created by GH0ST**

---

## ⚠️ Disclaimer / Zrzeczenie się odpowiedzialności

**English:**
This tool is for **educational purposes only**. Mass reporting can lead to a violation of Discord's Terms of Service and may result in a ban of your account. The creator (GH0ST) is not responsible for any misuse of this tool. Use it at your own risk.

**Polski:**
To narzędzie służy **wyłącznie do celów edukacyjnych**. Masowe zgłaszanie wiadomości może naruszać Warunki Korzystania z Usług Discord i prowadzić do blokady konta. Twórca (GH0ST) nie ponosi odpowiedzialności za niewłaściwe użycie tego narzędzia. Używasz go na własne ryzyko.

---

# 🇬🇧 English Documentation

### Features
*   **Cross-Platform:** Works seamlessly on Windows, Linux, and Android (Termux).
*   **Smart Input:** Automatically extracts Channel/Message IDs from pasted URLs.
*   **Colorful CLI:** Professional and easy-to-read interface.
*   **Optimized Speed:** Configured to avoid immediate rate limits (Error 429).
*   **Proxy Support:** (Planned feature)

### 📥 Installation & Usage

#### 📱 Termux (Android)
1.  Update packages and install dependencies:
    ```bash
    pkg update && pkg upgrade -y
    pkg install python git -y
    ```
2.  Clone the repository:
    ```bash
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
    *(Note: If you are using a local folder, simply `cd` into it)*
3.  Install Python requirements:
    ```bash
    python setup.py
    ```
4.  Run the bot:
    ```bash
    python main.py
    ```

#### 💻 Windows
1.  **Install Python:** Download and install Python 3.x from [python.org](https://www.python.org/). **Make sure to check "Add Python to PATH" during installation.**
2.  **Download Source:** Download the `.zip` file of this repository and extract it, or use Git:
    ```cmd
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
3.  **Install Requirements:**
    Open `cmd` or PowerShell in the bot folder and run:
    ```cmd
    python setup.py
    ```
4.  **Run:**
    ```cmd
    python main.py
    ```

#### 🐧 Linux / 🍎 macOS
1.  **Install Python:** Ensure you have Python 3 installed.
    *   Linux (Debian/Ubuntu): `sudo apt install python3 git -y`
    *   macOS (using Brew): `brew install python git`
2.  **Clone Repository:**
    ```bash
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
3.  **Install Dependencies:**
    ```bash
    python3 setup.py
    ```
4.  **Run:**
    ```bash
    python3 main.py
    ```

---

# 🇵🇱 Polska Dokumentacja

### Funkcje
*   **Wieloplatformowość:** Działa na Windows, Linux i Androidzie (Termux).
*   **Inteligentne wprowadzanie:** Automatycznie wyciąga ID kanału/wiadomości z wklejonych linków.
*   **Kolorowe CLI:** Profesjonalny i czytelny interfejs terminala.
*   **Zoptymalizowana prędkość:** Skonfigurowany tak, aby unikać szybkich blokad (Rate Limit / Error 429).

### 📥 Instalacja i Użycie

#### 📱 Termux (Android)
1.  Zaktualizuj [akiety i zainstaluj zależności:
    ```bash
    pkg update && pkg upgrade -y
    pkg install python git -y
    ```
2.  Pobierz repozytorium:
    ```bash
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
    *(Uwaga: Jeśli używasz lokalnego folderu, po prostu wejdź do niego komendą `cd`)*
3.  Zainstaluj wymagane biblioteki:
    ```bash
    python setup.py
    ```
4.  Uruchom bota:
    ```bash
    python main.py
    ```

#### 💻 Windows
1.  **Zainstaluj Python:** Pobierz i zainstaluj Python 3.x ze strony [python.org](https://www.python.org/). **Pamiętaj, aby zaznaczyć opcję "Add Python to PATH" podczas instalacji.**
2.  **Pobierz kod:** Ściągnij plik `.zip` z tym repozytorium i rozpakuj go, lub użyj Git:
    ```cmd
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
3.  **Zainstaluj biblioteki:**
    Otwórz `cmd` lub PowerShell w folderze z botem i wpisz:
    ```cmd
    python setup.py
    ```
4.  **Uruchom:**
    ```cmd
    python main.py
    ```

#### 🐧 Linux / 🍎 macOS
1.  **Zainstaluj Python:** Upewnij się, że masz zainstalowanego Pythona 3.
    *   Linux (Debian/Ubuntu): `sudo apt install python3 git -y`
    *   macOS (przez Brew): `brew install python git`
2.  **Pobierz repozytorium:**
    ```bash
    git clone https://github.com/hoki0/Discord-mass-report.git
    cd daily-reporter
    ```
3.  **Zainstaluj zależności:**
    ```bash
    python3 setup.py
    ```
4.  **Uruchom:**
    ```bash
    python3 main.py
    ```

---
© 2024 **GH0ST**. All rights reserved.
