import json
import os
import threading
import time
import random
import logging
import queue
import requests
from datetime import datetime

# --- Configuration & Styling ---
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# --- Logging Setup ---
logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Main:
    def __init__(self):
        self.sent = 0
        self.errors = 0
        self.GUILD_ID = None
        self.CHANNEL_ID = None
        self.TARGETS = [] # List of (message_id, reason_id) or just message_id
        self.REASON = None # Default reason
        
        self.tokens = []
        self.proxies = []
        self.running = True
        self.mode = None # 'single' or 'user'

    def _extract_id(self, text):
        text = text.strip()
        if not text.isdigit():
            parts = text.split('/')
            for part in reversed(parts):
                if part.isdigit():
                    return part
        return text

    def load_config(self):
        if os.path.exists('tokens.txt'):
            with open('tokens.txt', 'r') as f:
                self.tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not self.tokens and os.path.exists('Config.json'):
            try:
                with open('Config.json', 'r') as f:
                    data = json.load(f)
                    if data.get('discordToken'): self.tokens.append(data['discordToken'])
            except: pass
        
        if not self.tokens:
            token = input(f'{Colors.CYAN}[>]{Colors.RESET} Enter Discord Token: ')
            self.tokens.append(token)
            with open('Config.json', 'w') as f: json.dump({'discordToken': token}, f)

        print(f'{Colors.GREEN}[+] Loaded {len(self.tokens)} tokens.{Colors.RESET}')

        if os.path.exists('proxies.txt'):
            with open('proxies.txt', 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f'{Colors.GREEN}[+] Loaded {len(self.proxies)} proxies.{Colors.RESET}')

    def get_inputs(self):
        print(f'\n{Colors.MAGENTA}Select Mode:{Colors.RESET}')
        print(f'{Colors.BLUE}[1]{Colors.RESET} Spam Report Single Message')
        print(f'{Colors.BLUE}[2]{Colors.RESET} Report All Messages from User (Scrape)')
        
        mode = input(f'{Colors.CYAN}[>]{Colors.RESET} Choice: ')
        
        self.GUILD_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Guild ID: '))
        self.CHANNEL_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Channel ID: '))
        
        if mode == '1':
            self.mode = 'single'
            msg_id = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Message ID: '))
            self.TARGETS.append(msg_id)
        elif mode == '2':
            self.mode = 'user'
            user_id = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Target User ID: '))
            amount = int(input(f'{Colors.CYAN}[>]{Colors.RESET} Messages to scan (e.g. 100): '))
            self._scrape_messages(user_id, amount)
        else:
            print(f'{Colors.RED}[!] Invalid mode.{Colors.RESET}')
            os._exit(0)

        self._get_reason()

    def _get_reason(self):
        print(f'\n{Colors.MAGENTA}Select Report Reason:{Colors.RESET}')
        print(f'{Colors.BLUE}[1]{Colors.RESET} Illegal content')
        print(f'{Colors.BLUE}[2]{Colors.RESET} Harassment')
        print(f'{Colors.BLUE}[3]{Colors.RESET} Spam or phishing links')
        print(f'{Colors.BLUE}[4]{Colors.RESET} Self-harm')
        print(f'{Colors.BLUE}[5]{Colors.RESET} NSFW content')
        
        REASON = input(f'{Colors.CYAN}[>]{Colors.RESET} Reason: ')
        mapping = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
        self.REASON = mapping.get(REASON, 1) # Default to Harassment

    def _scrape_messages(self, user_id, limit):
        print(f'{Colors.YELLOW}[*] Scraping messages...{Colors.RESET}')
        headers = {'Authorization': self.tokens[0], 'Content-Type': 'application/json'}
        try:
            r = requests.get(
                f'https://discord.com/api/v9/channels/{self.CHANNEL_ID}/messages?limit={limit}',
                headers=headers
            )
            if r.status_code == 200:
                messages = r.json()
                count = 0
                for msg in messages:
                    if msg['author']['id'] == str(user_id):
                        self.TARGETS.append(msg['id'])
                        count += 1
                print(f'{Colors.GREEN}[+] Found {count} messages from user.{Colors.RESET}')
                if count == 0:
                    print(f'{Colors.RED}[!] No messages found from this user in the last {limit} messages.{Colors.RESET}')
                    os._exit(0)
            else:
                print(f'{Colors.RED}[!] Failed to scrape: {r.status_code} {r.text}{Colors.RESET}')
                os._exit(0)
        except Exception as e:
            print(f'{Colors.RED}[!] Scrape error: {e}{Colors.RESET}')
            os._exit(0)

    def _get_proxy(self):
        if not self.proxies: return None
        p = random.choice(self.proxies)
        return {'http': f'http://{p}', 'https': f'http://{p}'} if not p.startswith('http') else {'http': p, 'https': p}

    def _reporter(self, token):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': token
        }

        # If User Mode: Iterate targets once per token
        # If Single Mode: Loop target infinitely
        
        while self.running:
            for msg_id in self.TARGETS:
                if not self.running: break
                
                try:
                    payload = {
                        'channel_id': self.CHANNEL_ID,
                        'message_id': msg_id,
                        'guild_id': self.GUILD_ID,
                        'reason': self.REASON
                    }
                    
                    proxies = self._get_proxy()
                    r = requests.post(
                        'https://discordapp.com/api/v9/report',
                        json=payload, headers=headers, proxies=proxies, timeout=10
                    )
                    
                    if r.status_code == 201:
                        self.sent += 1
                        logging.info(f'Reported {msg_id} token={token[:5]}...')
                    elif r.status_code == 429:
                        wait = r.json().get('retry_after', 2)
                        logging.warning(f'Rate Limit: {wait}s')
                        time.sleep(float(wait))
                    elif r.status_code in [401, 403]:
                        print(f'{Colors.RED}[!] Status {r.status_code}{Colors.RESET}')
                        return # Kill thread
                    else:
                        self.errors += 1
                        logging.error(f'Fail {r.status_code}')

                    if self.mode == 'user':
                        time.sleep(random.uniform(0.5, 1.5)) # Don't rush user wipe
                    
                except Exception as e:
                    self.errors += 1
                    logging.error(f'Error: {e}')
                    time.sleep(2)
            
            if self.mode == 'user':
                # Token finished all targets
                break 

    def start(self):
        self.load_config()
        self.get_inputs()
        
        print(f'\n{Colors.MAGENTA}[*] Launching attack...{Colors.RESET}')
        threading.Thread(target=self._update_status, daemon=True).start()
        
        threads = []
        for token in self.tokens:
            t = threading.Thread(target=self._reporter, args=(token,))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(0.1)

        try:
            while any(t.is_alive() for t in threads):
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False

    def _update_status(self):
        while self.running:
            print(f'\r{Colors.YELLOW}[Running]{Colors.RESET} Sent: {Colors.GREEN}{self.sent}{Colors.RESET} Errors: {Colors.RED}{self.errors}{Colors.RESET}', end='')
            time.sleep(1)

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{Colors.RED}')
    print(r"""
  ____        _ _                               _            
 |  _ \  __ _(_) |_   _       _ __ ___ _ __   ___  _ __| |_ ___ _ __ 
 | | | |/ _` | | | | | |_____| '__/ _ \ '_ \ / _ \| '__| __/ _ \ '__|
 | |_| | (_| | | | |_| |_____| | |  __/ |_) | (_) | |  | ||  __/ |   
 |____/ \__,_|_|_|\__, |     |_|  \___| .__/ \___/|_|   \__\___|_|   
                  |___/               |_|                            
    """)
    print(f'          {Colors.WHITE}Created by GH0ST{Colors.RESET}')
    print(f'       {Colors.MAGENTA} "testowane na zwierzętach"{Colors.RESET}')
    print(f'       {Colors.MAGENTA}[Discord Reporter] - Advanced{Colors.RESET}\n')
    app = Main()
    app.start()
