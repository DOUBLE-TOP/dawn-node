import requests
import time

from src.models.exceptions import CaptchaError
from src.utils.logger import Logger


class Service2Captcha(Logger):
    def __init__(self, account):
        Logger.__init__(self)
        self.account = account
        self.api_key = self._get_api_key()

    @staticmethod
    def _get_api_key():
        with open('./data/settings.txt', 'r') as file:
            for line in file:
                if line.startswith('captchaapikey'):
                    return line.split('=', 1)[1].strip()
        raise Exception("2Captcha API key not found in settings.txt")

    def solve_captcha(self, base64_captcha_image: str):
        try:
            url = 'http://2captcha.com/in.php'
            params = {
                'key': self.api_key,
                'method': 'base64',
                'body': base64_captcha_image,
                'json': 1
            }

            response = requests.post(url, data=params)
            result = response.json()

            if result['status'] != 1:
                return f"Error: {result['request']}"

            captcha_id = result['request']

            self.logger_msg(self.account, f"Request with image was sent successfully.", 'success')

            url = 'http://2captcha.com/res.php'
            params = {
                'key': self.api_key,
                'action': 'get',
                'id': captcha_id,
                'json': 1
            }

            while True:
                response = requests.get(url, params=params)
                result = response.json()

                if result['status'] == 1:
                    self.logger_msg(self.account, f"The answer was received successfully.", 'success')
                    return result['request']

                if result['request'] == 'CAPCHA_NOT_READY':
                    self.logger_msg(self.account, f"The answer is not ready.", 'warning')
                    time.sleep(5)
                else:
                    self.logger_msg(self.account,
                                    f"Some error occurs. Error - {result}", 'error')
                    raise Exception(f"{result['request']}")

        except Exception as e:
            raise CaptchaError(f"Error 2captcha: {str(e)}.")
