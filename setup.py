import subprocess
import sys

try:
    import requests
    print("Module 'requests' is already installed.")
except ImportError:
    print("Installing 'requests'...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
        print("\nFinished.")
    except subprocess.CalledProcessError:
        print("\n[!] Automatic installation failed due to system restrictions (PEP 668).")
        print("Please install 'requests' manually using your package manager:")
        print("    sudo apt install python3-requests")
        print("Or create a virtual environment.")
