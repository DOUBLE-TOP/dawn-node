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
            self.email = data.get("Email") or None
            self.password = data.get("Password") or None
            self.proxy = data.get("Proxy") or None
            self.app_id = data.get("App_ID") or None
            self.token = data.get("Token") or None
            self.user_agent = data.get("User_Agent") or None
            self.total_earnings = data.get("Total_Earnings") or None

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
    return Account(email=data.get('Email'), password=data.get('Password'), proxy=data.get('Proxy'))
