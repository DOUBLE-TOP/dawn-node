import re
from random import randint

from src.models.user_agents import USER_AGENTS
from src.utils.file_manager import read_account


class Account:
    def __init__(self, email, password, proxy):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.app_id = None
        self.token = None
        self.user_agent = None
        self.total_earnings = None

    async def get_detailed_dict_for_account(self):
        data = await read_account(self.email)
        if len(data) > 0:
            self.app_id = data.get("App_ID") or None
            self.token = data.get("Token") or None
            self.user_agent = data.get("User_Agent") or USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
            self.total_earnings = data.get("Total_Earnings") or None
        else:
            self.user_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]

    async def account_to_dict(self) -> dict:
        return {
            "Email": self.email,
            "Password": self.password,
            "Proxy": self.proxy,
            "App_ID": self.app_id,
            "Token": self.token,
            "User_Agent": self.user_agent,
            "Total_Earnings": self.total_earnings
        }


async def default_dict_to_account(data) -> Account:
    def beautify_string(data_string):
        data_string = data_string.strip()
        data_string = re.sub('\\s+', ' ', data_string)
        return data_string
    return Account(email=beautify_string(data.get('Email')),
                   password=beautify_string(data.get('Password')),
                   proxy=beautify_string(data.get('Proxy')))
