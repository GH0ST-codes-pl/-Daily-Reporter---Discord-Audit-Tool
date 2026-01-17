import json
import os
import threading
import time

import requests


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
class Main:
    def __init__(self):
        self.sent = 0
        self.errors = 0
        self.GUILD_ID = None
        self.CHANNEL_ID = None
        self.MESSAGE_ID = None
        self.REASON = None
        self.TOKEN = None
        self.RESPONSES = {
            '401: Unauthorized': f'{Colors.RED}[!] Invalid Discord token.{Colors.RESET}',
            'Missing Access': f'{Colors.RED}[!] Missing access to channel or guild.{Colors.RESET}',
            'You need to verify your account in order to perform this action.': f'{Colors.RED}[!] Unverified.{Colors.RESET}'
        }

    def _extract_id(self, text):
        # Removes surrounding whitespace and handles URLs by taking the last segment
        text = text.strip()
        if not text.isdigit():
            # Try to grab the last numeric component if it's a URL-like string
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

        if REASON.upper() in ('1', 'ILLEGAL CONTENT'):
            self.REASON = 0
        elif REASON.upper() in ('2', 'HARASSMENT'):
            self.REASON = 1
        elif REASON.upper() in ('3', 'SPAM OR PHISHING LINKS'):
            self.REASON = 2
        elif REASON.upper() in ('4', 'SELF-HARM'):
            self.REASON = 3
        elif REASON.upper() in ('5', 'NSFW CONTENT'):
            self.REASON = 4
        else:
            print(f'\n{Colors.RED}[!] Reason invalid.{Colors.RESET}')
            print(f'{Colors.RED}[Discord Reporter] - Restart required{Colors.RESET}')
            input("Press Enter to exit...")
            os._exit(0)

    def _reporter(self):
        report = requests.post(
            'https://discordapp.com/api/v8/report', json={
                'channel_id': self.CHANNEL_ID,
                'message_id': self.MESSAGE_ID,
                'guild_id': self.GUILD_ID,
                'reason': self.REASON
            }, headers={
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'sv-SE',
                'User-Agent': 'Discord/21295 CFNetwork/1128.0.1 Darwin/19.6.0',
                'Content-Type': 'application/json',
                'Authorization': self.TOKEN
            }
        )
        if (status := report.status_code) == 201:
            self.sent += 1
            print(f'{Colors.GREEN}[!] Reported successfully.{Colors.RESET}')
        elif status in (401, 403):
            self.errors += 1
            print(self.RESPONSES[report.json()['message']])
        else:
            self.errors += 1
            print(f'{Colors.RED}[!] Error: {report.text} | Status Code: {status}{Colors.RESET}')

    def _update_status(self):
        while True:
            print(f'\r{Colors.YELLOW}[Discord Reporter]{Colors.RESET} - Sent: {Colors.GREEN}{self.sent}{Colors.RESET} | Errors: {Colors.RED}{self.errors}{Colors.RESET}    ', end='', flush=True)
            time.sleep(0.5)

    def _multi_threading(self):
        threading.Thread(target=self._update_status, daemon=True).start()
        while True:
            if threading.active_count() <= 5:
                threading.Thread(target=self._reporter).start()
                time.sleep(2)

    def setup(self):
        recognized = None
        if os.path.exists(config_json := 'Config.json'):
            with open(config_json, 'r') as f:
                try:
                    data = json.load(f)
                    self.TOKEN = data['discordToken']
                except (KeyError, json.decoder.JSONDecodeError):
                    recognized = False
                else:
                    recognized = True
        else:
            recognized = False

        if not recognized:
            self.TOKEN = input(f'{Colors.CYAN}[>]{Colors.RESET} Discord token: ')
            with open(config_json, 'w') as f:
                json.dump({'discordToken': self.TOKEN}, f)
        print()
        self._multi_threading()


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
    print(f'       {Colors.MAGENTA}[Discord Reporter] - Main Menu{Colors.RESET}\n')
    main = Main()
    main.get_inputs()
    main.setup()
