import json
import os
import threading
import time
import random
import logging
import queue
from datetime import datetime

import requests

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
        self.MESSAGE_ID = None
        self.REASON = None
        
        self.tokens = []
        self.proxies = []
        self.running = True

        self.RESPONSES = {
            '401: Unauthorized': f'{Colors.RED}[!] Invalid Discord token.{Colors.RESET}',
            'Missing Access': f'{Colors.RED}[!] Missing access to channel or guild.{Colors.RESET}',
            'You need to verify your account in order to perform this action.': f'{Colors.RED}[!] Unverified.{Colors.RESET}'
        }

    def _extract_id(self, text):
        text = text.strip()
        if not text.isdigit():
            parts = text.split('/')
            for part in reversed(parts):
                if part.isdigit():
                    return part
        return text

    def get_inputs(self):
        self.GUILD_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Guild ID: '))
        self.CHANNEL_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Channel ID: '))
        self.MESSAGE_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Message ID: '))
        
        REASON = input(
            f'\n{Colors.BLUE}[1]{Colors.RESET} Illegal content\n'
            f'{Colors.BLUE}[2]{Colors.RESET} Harassment\n'
            f'{Colors.BLUE}[3]{Colors.RESET} Spam or phishing links\n'
            f'{Colors.BLUE}[4]{Colors.RESET} Self-harm\n'
            f'{Colors.BLUE}[5]{Colors.RESET} NSFW content\n\n'
            f'{Colors.CYAN}[>]{Colors.RESET} Reason: '
        )

        mapping = {
            '1': 0, 'ILLEGAL CONTENT': 0,
            '2': 1, 'HARASSMENT': 1,
            '3': 2, 'SPAM OR PHISHING LINKS': 2,
            '4': 3, 'SELF-HARM': 3,
            '5': 4, 'NSFW CONTENT': 4
        }
        
        self.REASON = mapping.get(REASON.upper())
        if self.REASON is None:
            print(f'\n{Colors.RED}[!] Reason invalid.{Colors.RESET}')
            input("Press Enter to exit...")
            os._exit(0)

    def load_config(self):
        # Load Tokens
        if os.path.exists('tokens.txt'):
            with open('tokens.txt', 'r') as f:
                self.tokens = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Fallback to Config.json if tokens.txt is empty
        if not self.tokens:
            if os.path.exists('Config.json'):
                try:
                    with open('Config.json', 'r') as f:
                        data = json.load(f)
                        token = data.get('discordToken')
                        if token:
                            self.tokens.append(token)
                except:
                    pass
        
        if not self.tokens:
            token = input(f'{Colors.CYAN}[>]{Colors.RESET} Enter Discord Token (or populate tokens.txt): ')
            self.tokens.append(token)
            # Save to Config.json for convenience
            with open('Config.json', 'w') as f:
                json.dump({'discordToken': token}, f)

        print(f'{Colors.GREEN}[+] Loaded {len(self.tokens)} tokens.{Colors.RESET}')

        # Load Proxies
        if os.path.exists('proxies.txt'):
            with open('proxies.txt', 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if self.proxies:
            print(f'{Colors.GREEN}[+] Loaded {len(self.proxies)} proxies.{Colors.RESET}')
        else:
            print(f'{Colors.YELLOW}[!] No proxies found. Running in direct mode.{Colors.RESET}')

    def _get_proxy(self):
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        if not proxy.startswith('http'):
            return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        return {'http': proxy, 'https': proxy}

    def _reporter(self, token):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US',
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
            ]),
            'Content-Type': 'application/json',
            'Authorization': token
        }
        
        payload = {
            'channel_id': self.CHANNEL_ID,
            'message_id': self.MESSAGE_ID,
            'guild_id': self.GUILD_ID,
            'reason': self.REASON
        }

        while self.running:
            try:
                proxies = self._get_proxy()
                response = requests.post(
                    'https://discordapp.com/api/v9/report',
                    json=payload,
                    headers=headers,
                    proxies=proxies,
                    timeout=10
                )
                
                status = response.status_code
                
                if status == 201:
                    self.sent += 1
                    logging.info(f'Report sent via {token[:10]}... | Proxy: {proxies}')
                elif status == 429:
                    retry_after = response.json().get('retry_after', 2)
                    logging.warning(f'Rate limited. Waiting {retry_after}s.')
                    time.sleep(float(retry_after))
                    continue # Retry immediately after sleep
                elif status in (401, 403):
                    self.errors += 1
                    logging.error(f'Auth error {status} for token {token[:10]}...')
                    print(f'{Colors.RED}[!] Invalid Token or Access: {token[:10]}...{Colors.RESET}')
                    return # Stop this thread/token
                else:
                    self.errors += 1
                    logging.error(f'Error {status}: {response.text}')

                # Random sleep to avoid simple patterns if not rate limited
                time.sleep(random.uniform(1.5, 3.0))
                
            except Exception as e:
                self.errors += 1
                logging.error(f'Connection error: {e}')
                time.sleep(3)

    def _update_status(self):
        while self.running:
            print(f'\r{Colors.YELLOW}[Running]{Colors.RESET} - Sent: {Colors.GREEN}{self.sent}{Colors.RESET} | Errors: {Colors.RED}{self.errors}{Colors.RESET} | Threads: {threading.active_count()-1}    ', end='', flush=True)
            time.sleep(0.5)

    def start(self):
        self.load_config()
        self.get_inputs()
        
        print(f'\n{Colors.MAGENTA}[*] Starting threads...{Colors.RESET}')
        
        # Start status thread
        threading.Thread(target=self._update_status, daemon=True).start()
        
        # Start reporter threads (one per token)
        threads = []
        for token in self.tokens:
            t = threading.Thread(target=self._reporter, args=(token,))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(0.1) # Stagger starts

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print(f'\n{Colors.RED}[!] Stopping...{Colors.RESET}')

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
    print(f'       {Colors.MAGENTA}[Discord Reporter] - Advanced{Colors.RESET}\n')
    
    app = Main()
    app.start()
