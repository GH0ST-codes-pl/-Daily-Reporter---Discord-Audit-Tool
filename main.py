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
        print(f'{Colors.BLUE}[3]{Colors.RESET} Report Entire Server/Guild')
        
        mode = input(f'{Colors.CYAN}[>]{Colors.RESET} Choice: ')
        
        self.GUILD_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Guild ID: '))
        
        if mode == '1':
            self.mode = 'single'
            self.CHANNEL_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Channel ID: '))
            msg_id = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Message ID: '))
            self.TARGETS.append({'message_id': msg_id, 'channel_id': self.CHANNEL_ID})
        elif mode == '2':
            self.mode = 'user'
            user_id = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Target User ID: '))
            keyword = input(f'{Colors.CYAN}[>]{Colors.RESET} Filter by keyword (press Enter to skip): ').strip()
            if not keyword: keyword = None
            
            print(f'\n{Colors.MAGENTA}Scraping Mode:{Colors.RESET}')
            print(f'{Colors.BLUE}[1]{Colors.RESET} Scan Single Channel')
            print(f'{Colors.BLUE}[2]{Colors.RESET} Scan All Server Channels')
            scrape_mode = input(f'{Colors.CYAN}[>]{Colors.RESET} Choice: ')
            
            if scrape_mode == '1':
                self.CHANNEL_ID = self._extract_id(input(f'{Colors.CYAN}[>]{Colors.RESET} Channel ID: '))
                amount = int(input(f'{Colors.CYAN}[>]{Colors.RESET} Messages to scan (e.g. 10000): '))
                self._scrape_messages(user_id, amount, keyword)
            elif scrape_mode == '2':
                self.CHANNEL_ID = None
                amount = int(input(f'{Colors.CYAN}[>]{Colors.RESET} Messages per channel (e.g. 5000): '))
                self._scrape_all_channels(user_id, amount, keyword)
            else:
                print(f'{Colors.RED}[!] Invalid scraping mode.{Colors.RESET}')
                os._exit(0)
        elif mode == '3':
            self.mode = 'guild'
            self.CHANNEL_ID = None  # Not needed for guild reports
            print(f'{Colors.YELLOW}[*] Guild reporting mode selected.{Colors.RESET}')
        else:
            print(f'{Colors.RED}[!] Invalid mode.{Colors.RESET}')
            os._exit(0)

        self._get_reason()

    def _get_reason(self):
        if self.mode == 'guild':
            print(f'\n{Colors.MAGENTA}Select Guild Report Reason:{Colors.RESET}')
            print(f'{Colors.BLUE}[1]{Colors.RESET} Illegal content')
            print(f'{Colors.BLUE}[2]{Colors.RESET} Harassment')
            print(f'{Colors.BLUE}[3]{Colors.RESET} Spam or phishing')
            print(f'{Colors.BLUE}[4]{Colors.RESET} Raid or brigading')
            print(f'{Colors.BLUE}[5]{Colors.RESET} NSFW content')
            
            REASON = input(f'{Colors.CYAN}[>]{Colors.RESET} Reason: ')
            mapping = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
            self.REASON = mapping.get(REASON, 1)
        else:
            print(f'\n{Colors.MAGENTA}Select Report Reason:{Colors.RESET}')
            print(f'{Colors.BLUE}[1]{Colors.RESET} Illegal content')
            print(f'{Colors.BLUE}[2]{Colors.RESET} Harassment')
            print(f'{Colors.BLUE}[3]{Colors.RESET} Spam or phishing links')
            print(f'{Colors.BLUE}[4]{Colors.RESET} Self-harm')
            print(f'{Colors.BLUE}[5]{Colors.RESET} NSFW content')
            
            REASON = input(f'{Colors.CYAN}[>]{Colors.RESET} Reason: ')
            mapping = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
            self.REASON = mapping.get(REASON, 1) # Default to Harassment

    def _scrape_messages(self, user_id, limit, keyword=None):
        print(f'{Colors.YELLOW}[*] Scraping messages...{Colors.RESET}')
        headers = {'Authorization': self.tokens[0], 'Content-Type': 'application/json'}
        
        all_messages = []
        last_message_id = None
        fetched = 0
        
        try:
            # Fetch in batches of 100 (Discord API limit)
            while fetched < limit:
                batch_size = min(100, limit - fetched)
                url = f'https://discord.com/api/v9/channels/{self.CHANNEL_ID}/messages?limit={batch_size}'
                if last_message_id:
                    url += f'&before={last_message_id}'
                
                r = requests.get(url, headers=headers)
                
                if r.status_code == 200:
                    messages = r.json()
                    if not messages:  # No more messages
                        break
                    
                    all_messages.extend(messages)
                    fetched += len(messages)
                    last_message_id = messages[-1]['id']
                    
                    print(f'{Colors.YELLOW}[*] Fetched {fetched}/{limit} messages...{Colors.RESET}')
                    time.sleep(0.5)  # Rate limit protection
                elif r.status_code == 429:
                    wait = r.json().get('retry_after', 2)
                    print(f'{Colors.YELLOW}[*] Rate limited, waiting {wait}s...{Colors.RESET}')
                    time.sleep(float(wait))
                else:
                    print(f'{Colors.RED}[!] Failed to scrape: {r.status_code} {r.text}{Colors.RESET}')
                    os._exit(0)
            
            # Filter messages from target user
            count = 0
            for msg in all_messages:
                if msg['author']['id'] == str(user_id):
                    if keyword and keyword.lower() not in msg['content'].lower(): continue
                    self.TARGETS.append({'message_id': msg['id'], 'channel_id': self.CHANNEL_ID})
                    count += 1
            
            print(f'{Colors.GREEN}[+] Found {count} messages from user in {fetched} total messages.{Colors.RESET}')
            if count == 0:
                print(f'{Colors.RED}[!] No messages found from this user in the last {fetched} messages.{Colors.RESET}')
                os._exit(0)
                
        except KeyboardInterrupt:
            print(f'\n{Colors.RED}[!] Scrape stopped by user.{Colors.RESET}')
            os._exit(0)
        except Exception as e:
            print(f'{Colors.RED}[!] Scrape error: {e}{Colors.RESET}')
            os._exit(0)

    def _scrape_all_channels(self, user_id, limit_per_channel, keyword=None):
        """Scrape messages from user across ALL channels in the guild"""
        print(f'{Colors.YELLOW}[*] Fetching all channels in guild...{Colors.RESET}')
        headers = {'Authorization': self.tokens[0], 'Content-Type': 'application/json'}
        
        try:
            # Get all channels in the guild
            r = requests.get(
                f'https://discord.com/api/v9/guilds/{self.GUILD_ID}/channels',
                headers=headers
            )
            
            if r.status_code != 200:
                print(f'{Colors.RED}[!] Failed to fetch channels: {r.status_code} {r.text}{Colors.RESET}')
                os._exit(0)
            
            channels = r.json()
            # Filter only text channels (type 0) and announcement channels (type 5)
            text_channels = [ch for ch in channels if ch.get('type') in [0, 5]]
            
            print(f'{Colors.GREEN}[+] Found {len(text_channels)} text channels. Scanning...{Colors.RESET}')
            
            total_found = 0
            for idx, channel in enumerate(text_channels, 1):
                channel_id = channel['id']
                channel_name = channel.get('name', 'unknown')
                
                print(f'{Colors.CYAN}[{idx}/{len(text_channels)}]{Colors.RESET} Scanning #{channel_name}...')
                
                # Scrape this channel
                all_messages = []
                last_message_id = None
                fetched = 0
                
                try:
                    while fetched < limit_per_channel:
                        batch_size = min(100, limit_per_channel - fetched)
                        url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={batch_size}'
                        if last_message_id:
                            url += f'&before={last_message_id}'
                        
                        r = requests.get(url, headers=headers)
                        
                        if r.status_code == 200:
                            messages = r.json()
                            if not messages:
                                break
                            
                            all_messages.extend(messages)
                            fetched += len(messages)
                            last_message_id = messages[-1]['id']
                            time.sleep(0.3)
                        elif r.status_code == 429:
                            wait = r.json().get('retry_after', 2)
                            print(f'{Colors.YELLOW}[*] Rate limited, waiting {wait}s...{Colors.RESET}')
                            time.sleep(float(wait))
                        elif r.status_code == 403:
                            print(f'{Colors.YELLOW}[!] No access to #{channel_name}, skipping...{Colors.RESET}')
                            break
                        else:
                            break
                    
                    # Filter messages from target user in this channel
                    channel_count = 0
                    for msg in all_messages:
                        if msg['author']['id'] == str(user_id):
                            if keyword and keyword.lower() not in msg['content'].lower(): continue
                            self.TARGETS.append({'message_id': msg['id'], 'channel_id': channel_id})
                            channel_count += 1
                            total_found += 1
                    
                    if channel_count > 0:
                        print(f'{Colors.GREEN}  └─ Found {channel_count} messages from user{Colors.RESET}')
                    
                except KeyboardInterrupt:
                    print(f'\n{Colors.RED}[!] Scrape stopped by user.{Colors.RESET}')
                    os._exit(0)
                except Exception as e:
                    print(f'{Colors.YELLOW}[!] Error scanning #{channel_name}: {e}{Colors.RESET}')
                    continue
            
            print(f'{Colors.GREEN}[+] Total: Found {total_found} messages from user across {len(text_channels)} channels.{Colors.RESET}')
            
            if total_found == 0:
                print(f'{Colors.RED}[!] No messages found from this user in any channel.{Colors.RESET}')
                os._exit(0)
                
        except Exception as e:
            print(f'{Colors.RED}[!] Error fetching channels: {e}{Colors.RESET}')
            os._exit(0)

    def _get_proxy(self):
        if not self.proxies: return None
        p = random.choice(self.proxies)
        return {'http': f'http://{p}', 'https': f'http://{p}'} if not p.startswith('http') else {'http': p, 'https': p}

    def _guild_reporter(self, token):
        """Report guild owner (server owner's profile)"""
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': token
        }

        # First, get guild info to find owner
        owner_id = None
        try:
            r = requests.get(
                f'https://discord.com/api/v9/guilds/{self.GUILD_ID}',
                headers=headers
            )
            if r.status_code == 200:
                guild_data = r.json()
                owner_id = guild_data.get('owner_id')
                print(f'{Colors.GREEN}[+] Found guild owner: {owner_id}{Colors.RESET}')
            else:
                print(f'{Colors.RED}[!] Failed to fetch guild info: {r.status_code}{Colors.RESET}')
                return
        except Exception as e:
            print(f'{Colors.RED}[!] Error fetching guild: {e}{Colors.RESET}')
            return

        if not owner_id:
            print(f'{Colors.RED}[!] Could not find guild owner{Colors.RESET}')
            return

        # Now report the owner's profile repeatedly
        while self.running:
            try:
                payload = {
                    'guild_id': self.GUILD_ID,
                    'user_id': owner_id,
                    'reason': self.REASON
                }
                
                proxies = self._get_proxy()
                r = requests.post(
                    'https://discordapp.com/api/v9/report',
                    json=payload, headers=headers, proxies=proxies, timeout=10
                )
                
                if r.status_code == 201:
                    self.sent += 1
                    logging.info(f'Reported guild owner {owner_id} in guild {self.GUILD_ID} token={token[:5]}...')
                elif r.status_code == 429:
                    wait = r.json().get('retry_after', 2)
                    logging.warning(f'Rate Limit: {wait}s')
                    time.sleep(float(wait))
                    continue  # Retry after waiting
                elif r.status_code in [401, 403]:
                    print(f'{Colors.RED}[!] Token invalid/forbidden {r.status_code}{Colors.RESET}')
                    return  # Kill thread
                else:
                    self.errors += 1
                    logging.error(f'Guild owner report fail {r.status_code}: {r.text}')

                time.sleep(random.uniform(1.0, 2.0))  # Delay between reports
                
            except Exception as e:
                self.errors += 1
                logging.error(f'Guild owner report error: {e}')
                time.sleep(2)

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
            for target in self.TARGETS:
                if not self.running: break
                
                try:
                    payload = {
                        'channel_id': target['channel_id'],
                        'message_id': target['message_id'],
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
                        logging.info(f"Reported {target['message_id']} token={token[:5]}...")
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
            if self.mode == 'guild':
                t = threading.Thread(target=self._guild_reporter, args=(token,))
            else:
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
