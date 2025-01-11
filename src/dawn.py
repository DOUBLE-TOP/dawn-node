import decimal

from datetime import datetime

from src.base_client import BaseClient
from src.models.account import Account
from src.models.exceptions import SoftwareException
from src.utils.captcha import Service2Captcha
from src.utils.file_manager import update_variables_in_file
from src.utils.logger import Logger


class DawnClient(Logger, BaseClient):

    def __init__(self, account: Account):
        Logger.__init__(self)
        BaseClient.__init__(self, account)
        self.account = account

    async def login(self, force: bool = False):
        try:
            if 'None' in str(self.account.token) or 'None' in str(self.account.app_id) or force:
                self.logger_msg(self.account, "The token is absent or it's expired.", 'success')
                if 'None' in str(self.account.app_id):
                    await self.get_app_id()
                puzzle_id = await self.get_puzzle_id()
                puzzle_image = await self.get_puzzle_image(puzzle_id)
                solver = Service2Captcha(self.account)
                puzzle_answer = solver.solve_captcha(puzzle_image)
                await self.get_token(puzzle_id, puzzle_answer)
                if "None" in self.account.token:
                    raise SoftwareException()
        except SoftwareException:
            self.logger_msg(self.account,
                            "The user was not logged in successfully. The token is absent.", 'warning')

    async def get_token(self, puzzle_id, puzzle_answer):
        try:
            login_url = 'https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2'
            login_params = {'appid': self.account.app_id}
            login_payload = {
                "username": self.account.email,
                "password": self.account.password,
                "logindata":
                    {"_v": {"version": "1.1.2"},
                     "datetime": str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')},
                "puzzle_id": puzzle_id,
                "ans": puzzle_answer}

            response = await self.make_request(method="POST", url=login_url, params=login_params,
                                               json=login_payload)
            self.account.token = f"Bearer {response.get('data').get('token')}"

            self.logger_msg(self.account, "The user is logged in successfully.", 'success')
        except SoftwareException as e:
            self.logger_msg(self.account,
                            "The user was not logged in successfully. "
                            f"Account token - {self.account.token}. Error - {e}", 'warning')

    async def get_points(self) -> decimal:
        try:
            url = 'https://www.aeropres.in/api/atom/v1/userreferral/getpoint'
            params = {'appid': self.account.app_id}
            headers = {'authorization': self.account.token}

            response = await self.make_request(method="GET", url=url, params=params,
                                               headers=headers)

            points = 0.00

            if response['message'] == "success":
                points = round(response.get('data').get('referralPoint').get('commission') +
                               response.get('data').get('rewardPoint').get('points') +
                               response.get('data').get('rewardPoint').get('registerpoints') +
                               response.get('data').get('rewardPoint').get('signinpoints') +
                               response.get('data').get('rewardPoint').get('twitter_x_id_points') +
                               response.get('data').get('rewardPoint').get('discordid_points') +
                               response.get('data').get('rewardPoint').get('telegramid_points') +
                               response.get('data').get('rewardPoint').get('bonus_points'), 1)

            self.account.total_earnings = points

            if response.get('data').get('rewardPoint').get('twitter_x_id_points') < 1:
                await self.get_twitter_points()

            if response.get('data').get('rewardPoint').get('discordid_points') < 1:
                await self.get_discord_points()

            if response.get('data').get('rewardPoint').get('telegramid_points') < 1:
                await self.get_telegram_points()

            self.logger_msg(self.account, f"Current points - {points}", 'success')
            return 0
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Request for getting points was failed by some reasons. Error - {e}", 'warning')
            return 1

    async def keep_alive(self):
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive'
            params = {'appid': self.account.app_id}
            headers = {'authorization': self.account.token}
            payload = {
                "username": self.account.email,
                "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp",
                "numberoftabs": 0,
                "_v": "1.1.2"}

            await self.make_request(method="POST", url=url, params=params, json=payload,
                                    headers=headers)

            self.logger_msg(self.account, "Keep alive recorded!", 'success')
            return 0
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Keep alive was not recorded by some reasons. Error - {e}", 'warning')
            return 1

    async def get_app_id(self):
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/appid/getappid'
            params = {'app_v': '1.1.2'}
    
            response = await self.make_request(method="GET", url=url, params=params)
            app_id = response['data'].get('appid')
            if 'None' in str(app_id):
                raise SoftwareException()
            else:
                self.account.app_id = app_id
                await update_variables_in_file(self, self.account, await self.account.account_to_dict())
                self.logger_msg(self.account,
                                f"Application ID received successfully. ID - {app_id}", 'success')
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Application ID was not received successfully. {e}", 'warning')

    async def get_puzzle_id(self) -> str:
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle'
            params = {'appid': self.account.app_id}

            response = await self.make_request(method="GET", url=url, params=params)
            puzzle_id = response.get('puzzle_id')

            self.logger_msg(self.account,
                            f"Puzzle ID received successfully. ID - {puzzle_id}", 'success')

            return puzzle_id
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Puzzle ID was not received successfully. {e}", 'warning')

    async def get_puzzle_image(self, puzzle_id: str) -> str:
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image'
            params = {'puzzle_id': puzzle_id, 'appid': self.account.app_id}

            response = await self.make_request(method="GET", url=url, params=params)
            img = response.get('imgBase64')

            self.logger_msg(self.account,
                            f"Puzzle image in base64 format received successfully.",
                            'success')

            return img
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Puzzle image in base64 format was not received successfully. {e}",
                            'warning')

    async def get_twitter_points(self):
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/profile/update'
            params = {'appid': self.account.app_id}
            headers = {'authorization': self.account.token}
            payload = {"twitter_x_id": "twitter_x_id"}

            await self.make_request(method="POST", url=url, params=params, headers=headers,
                                    json=payload)

            self.logger_msg(self.account, f"Twitter points requested successfully.", 'success')
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Twitter points was not requested successfully. {e}", 'warning')

    async def get_discord_points(self):
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/profile/update'
            params = {'appid': self.account.app_id}
            headers = {'authorization': self.account.token}
            payload = {"discordid": "discordid"}

            await self.make_request(method="POST", url=url, params=params, headers=headers,
                                    json=payload)

            self.logger_msg(self.account, f"Discord points requested successfully.", 'success')
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Discord points was not requested successfully. {e}", 'warning')

    async def get_telegram_points(self):
        try:
            url = 'https://www.aeropres.in/chromeapi/dawn/v1/profile/update'
            params = {'appid': self.account.app_id}
            headers = {'authorization': self.account.token}
            payload = {"telegramid": "telegramid"}

            await self.make_request(method="POST", url=url, params=params, headers=headers,
                                    json=payload)

            self.logger_msg(self.account, "Telegram points requested successfully.", 'success')
        except SoftwareException as e:
            self.logger_msg(self.account,
                            f"Telegram points was not requested successfully. {e}", 'warning')
