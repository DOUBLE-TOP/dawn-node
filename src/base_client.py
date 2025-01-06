import asyncio
import re
import ssl
from abc import ABC
from random import randint

import aiohttp
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from src.models.account import Account
from src.models.exceptions import SoftwareException
from src.models.user_agents import USER_AGENTS


class BaseClient(ABC):
    def __init__(self, account: Account):
        self.account = account
        self.session = ClientSession(
            connector=ProxyConnector.from_url(f'{account.proxy}',
                                              ssl=ssl.create_default_context(), verify_ssl=True))

    async def make_request(self, method: str = 'GET', url: str = None, params: dict = None, headers: dict = None,
                           data: str = None, json: dict = None, module_name: str = 'Request'):

        total_time = 0
        timeout = 360
        while True:
            try:
                request_headers = await self.generate_headers(headers)
                async with self.session.request(
                        method=method, url=url, headers=request_headers,
                        data=data, params=params, json=json) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        if isinstance(data, dict):
                            success = data.get('success') or True
                        elif isinstance(data, list) and isinstance(data[0], dict):
                            success = data[0].get('success') or True

                        if success:
                            return data
                        else:
                            raise SoftwareException(
                                f"Bad request to {self.__class__.__name__}({module_name}) API: {data['message']}")

                    raise SoftwareException(
                        f"Bad request to {self.__class__.__name__}({module_name}) API: {await response.text()}")
            except aiohttp.client_exceptions.ServerDisconnectedError as error:
                total_time += 15
                await asyncio.sleep(15)
                if total_time > timeout:
                    raise SoftwareException(error)
                continue
            except Exception as error:
                if 'Error code 502' in str(error):
                    raise SoftwareException("Cloudflare 502 error")
                if 'Cannot GET /chromeapi/dawn/v1/' in str(error):
                    raise SoftwareException("Server error.")
                raise SoftwareException(error)

    async def generate_headers(self, extra_headers: dict = None):
        if 'None' in str(self.account.user_agent):
            self.account.user_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]

        ua_pattern = re.compile(
            r'Mozilla/5.0 \(([^)]+)\) AppleWebKit/([\d.]+) \(KHTML, like Gecko\) Chrome/([\d.]+) Safari/([\d.]+)'
        )
        # Match the User-Agent string
        match = ua_pattern.match(self.account.user_agent)

        # If not matched, raise an exception
        if not match:
            raise ValueError("User-Agent format not recognized")

        # Extract platform and version information
        platform = match.group(1).strip()
        chrome_version = match.group(3).split('.')[0]

        # Calculate platform
        sec_ua_platform = ""
        sec_ch_ua = ""
        if "Windows" in platform:
            sec_ua_platform = "Windows"
            sec_ch_ua = f'"Not/A)Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"'
        if "Linux" in platform:
            sec_ua_platform = "Linux"
            sec_ch_ua = f'"Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}", "Not-A.Brand";v="99"'
        if "Macintosh" in platform:
            sec_ua_platform = "macOS"
            sec_ch_ua = f'"Not_A Brand";v="8", "Chromium";v="{chrome_version}", "Google Chrome";v="{chrome_version}"'
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp',
            'priority': 'u=1, i',
            'sec-ch-ua': f'{sec_ch_ua}',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{sec_ua_platform}"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': self.account.user_agent
        }

        if extra_headers:
            headers = dict(headers, **extra_headers)
        return headers
